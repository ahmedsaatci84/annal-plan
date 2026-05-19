from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods

from apps.core.middleware import log_action, AuditLogMiddleware
from apps.plans.models import AnnualPlan, Goal, Activity
from apps.plans.forms import ActivityForm, ActivityProgressForm
from .plan_views import _check_plan_access


@login_required
def activity_create(request, plan_pk, goal_pk):
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    goal = get_object_or_404(Goal, pk=goal_pk, plan=plan)
    _check_plan_access(request.user, plan)
    if not request.user.profile.can_edit_plan(plan):
        raise PermissionDenied
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            last_seq = goal.activities.order_by('-sequence').values_list('sequence', flat=True).first() or 0
            activity = form.save(commit=False)
            activity.goal = goal
            activity.sequence = last_seq + 1
            activity.code = f'{goal.sequence}-{activity.sequence}'
            activity.save()
            ip = AuditLogMiddleware.get_client_ip(request)
            log_action(request.user, 'CREATE', 'Activity', activity, ip_address=ip)
            messages.success(request, 'تم إضافة النشاط بنجاح.')
            return redirect('plans:goals', plan_pk=plan.pk)
    else:
        form = ActivityForm()
    return render(request, 'plans/activity_form.html', {
        'form': form, 'plan': plan, 'goal': goal, 'title': 'إضافة نشاط'
    })


@login_required
def activity_edit(request, plan_pk, goal_pk, activity_pk):
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    goal = get_object_or_404(Goal, pk=goal_pk, plan=plan)
    activity = get_object_or_404(Activity, pk=activity_pk, goal=goal)
    _check_plan_access(request.user, plan)

    # After approval, only progress update is allowed
    if plan.is_locked():
        form_class = ActivityProgressForm
    elif request.user.profile.can_edit_plan(plan):
        form_class = ActivityForm
    else:
        raise PermissionDenied

    if request.method == 'POST':
        form = form_class(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            ip = AuditLogMiddleware.get_client_ip(request)
            log_action(request.user, 'UPDATE', 'Activity', activity, ip_address=ip)
            messages.success(request, 'تم تحديث النشاط بنجاح.')
            return redirect('plans:goals', plan_pk=plan.pk)
    else:
        form = form_class(instance=activity)
    return render(request, 'plans/activity_form.html', {
        'form': form, 'plan': plan, 'goal': goal,
        'activity': activity, 'title': 'تعديل النشاط'
    })


@login_required
@require_http_methods(['PATCH', 'POST'])
def activity_update_progress(request, plan_pk, goal_pk, activity_pk):
    """AJAX endpoint: update actual_completion_pct."""
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    activity = get_object_or_404(Activity, pk=activity_pk, goal__plan=plan)
    _check_plan_access(request.user, plan)

    # Allowed for approved plans (progress updates) or draft plans
    if plan.status not in (AnnualPlan.STATUS_APPROVED, AnnualPlan.STATUS_DRAFT,
                           AnnualPlan.STATUS_REJECTED):
        return JsonResponse({'error': 'غير مسموح'}, status=403)

    import json
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, AttributeError):
        from django.http import QueryDict
        data = request.POST

    pct = data.get('actual_completion_pct')
    status_val = data.get('activity_status')
    try:
        pct = int(pct)
        if not 0 <= pct <= 100:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({'error': 'قيمة غير صحيحة'}, status=400)

    activity.actual_completion_pct = pct
    if status_val in dict(Activity.STATUS_CHOICES):
        activity.activity_status = status_val
    else:
        activity.auto_update_status()
    activity.save(update_fields=['actual_completion_pct', 'activity_status', 'updated_at'])

    return JsonResponse({
        'actual_completion_pct': activity.actual_completion_pct,
        'activity_status': activity.activity_status,
        'goal_completion_pct': activity.goal.completion_pct(),
    })


@login_required
@require_POST
def activity_delete(request, plan_pk, goal_pk, activity_pk):
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    goal = get_object_or_404(Goal, pk=goal_pk, plan=plan)
    activity = get_object_or_404(Activity, pk=activity_pk, goal=goal)
    _check_plan_access(request.user, plan)
    if not request.user.profile.can_edit_plan(plan):
        raise PermissionDenied
    ip = AuditLogMiddleware.get_client_ip(request)
    log_action(request.user, 'DELETE', 'Activity', activity, ip_address=ip)
    activity.delete()
    messages.success(request, 'تم حذف النشاط بنجاح.')
    return redirect('plans:goals', plan_pk=plan.pk)
