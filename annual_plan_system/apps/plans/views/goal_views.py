from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST

from apps.core.middleware import log_action, AuditLogMiddleware
from apps.plans.models import AnnualPlan, Goal
from apps.plans.forms import GoalForm
from .plan_views import _check_plan_access


@login_required
def goal_list(request, plan_pk):
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    _check_plan_access(request.user, plan)
    goals = plan.goals.prefetch_related('activities').order_by('sequence')
    return render(request, 'plans/sections/goals.html', {
        'plan': plan,
        'goals': goals,
        'can_edit': request.user.profile.can_edit_plan(plan),
    })


@login_required
def goal_create(request, plan_pk):
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    _check_plan_access(request.user, plan)
    if not request.user.profile.can_edit_plan(plan):
        raise PermissionDenied
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            last_seq = plan.goals.order_by('-sequence').values_list('sequence', flat=True).first() or 0
            goal = form.save(commit=False)
            goal.plan = plan
            goal.sequence = last_seq + 1
            goal.code = f'({goal.sequence})'
            goal.save()
            ip = AuditLogMiddleware.get_client_ip(request)
            log_action(request.user, 'CREATE', 'Goal', goal, ip_address=ip)
            messages.success(request, 'تم إضافة الهدف بنجاح.')
            return redirect('plans:goals', plan_pk=plan.pk)
    else:
        form = GoalForm()
    return render(request, 'plans/goal_form.html', {
        'form': form, 'plan': plan, 'title': 'إضافة هدف جديد'
    })


@login_required
def goal_edit(request, plan_pk, goal_pk):
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    goal = get_object_or_404(Goal, pk=goal_pk, plan=plan)
    _check_plan_access(request.user, plan)
    if not request.user.profile.can_edit_plan(plan):
        raise PermissionDenied
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            ip = AuditLogMiddleware.get_client_ip(request)
            log_action(request.user, 'UPDATE', 'Goal', goal, ip_address=ip)
            messages.success(request, 'تم تحديث الهدف بنجاح.')
            return redirect('plans:goals', plan_pk=plan.pk)
    else:
        form = GoalForm(instance=goal)
    return render(request, 'plans/goal_form.html', {
        'form': form, 'plan': plan, 'goal': goal, 'title': 'تعديل الهدف'
    })


@login_required
@require_POST
def goal_delete(request, plan_pk, goal_pk):
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    goal = get_object_or_404(Goal, pk=goal_pk, plan=plan)
    _check_plan_access(request.user, plan)
    if not request.user.profile.can_edit_plan(plan):
        raise PermissionDenied
    ip = AuditLogMiddleware.get_client_ip(request)
    log_action(request.user, 'DELETE', 'Goal', goal, ip_address=ip)
    goal.delete()
    # Re-sequence remaining goals
    for i, g in enumerate(plan.goals.order_by('sequence'), start=1):
        if g.sequence != i:
            g.sequence = i
            g.code = f'({i})'
            g.save(update_fields=['sequence', 'code'])
    messages.success(request, 'تم حذف الهدف بنجاح.')
    return redirect('plans:goals', plan_pk=plan.pk)
