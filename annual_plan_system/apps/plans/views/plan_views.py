from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST

from apps.core.middleware import log_action, AuditLogMiddleware
from apps.plans.models import AnnualPlan, SwotAnalysis, PlanWorkflowLog
from apps.plans.forms import PlanHeaderForm, WorkflowCommentForm


@login_required
def plan_list(request):
    profile = request.user.profile
    if profile.is_admin():
        plans = AnnualPlan.objects.select_related('formation', 'created_by').order_by('-plan_year')
    elif profile.is_manager():
        formation = profile.formation
        ids = [formation.id] if formation else []
        plans = AnnualPlan.objects.filter(formation_id__in=ids).select_related('formation')
    else:
        plans = AnnualPlan.objects.filter(
            formation=profile.formation
        ).select_related('formation')

    year_filter = request.GET.get('year')
    status_filter = request.GET.get('status')
    if year_filter:
        plans = plans.filter(plan_year=year_filter)
    if status_filter:
        plans = plans.filter(status=status_filter)

    return render(request, 'plans/plan_list.html', {
        'plans': plans,
        'status_choices': AnnualPlan.STATUS_CHOICES,
        'selected_year': year_filter,
        'selected_status': status_filter,
    })


@login_required
def plan_create(request):
    profile = request.user.profile
    if profile.role not in ('ADMIN', 'MANAGER', 'ORGANIZER'):
        raise PermissionDenied
    if request.method == 'POST':
        form = PlanHeaderForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.created_by = request.user
            plan.save()
            # Create default SWOT
            SwotAnalysis.objects.get_or_create(plan=plan)
            ip = AuditLogMiddleware.get_client_ip(request)
            log_action(request.user, 'CREATE', 'AnnualPlan', plan, ip_address=ip)
            messages.success(request, 'تم إنشاء الخطة بنجاح.')
            return redirect('plans:detail', pk=plan.pk)
    else:
        from django.utils import timezone
        form = PlanHeaderForm(initial={'plan_year': timezone.now().year})
        if profile.formation and not profile.is_admin():
            form.fields['formation'].initial = profile.formation.id
    return render(request, 'plans/plan_form.html', {'form': form, 'title': 'إنشاء خطة سنوية'})


@login_required
def plan_detail(request, pk):
    plan = get_object_or_404(
        AnnualPlan.objects.select_related('formation', 'created_by'),
        pk=pk
    )
    _check_plan_access(request.user, plan)
    swot, _ = SwotAnalysis.objects.get_or_create(plan=plan)
    goals = plan.goals.prefetch_related('activities').order_by('sequence')
    risks = plan.risks.all()
    workflow_logs = plan.workflow_logs.select_related('performed_by').order_by('-created_at')

    return render(request, 'plans/plan_detail.html', {
        'plan': plan,
        'swot': swot,
        'goals': goals,
        'risks': risks,
        'workflow_logs': workflow_logs,
        'can_edit': request.user.profile.can_edit_plan(plan),
        'can_review': request.user.profile.can_review_plan(plan),
    })


@login_required
def plan_edit(request, pk):
    plan = get_object_or_404(AnnualPlan, pk=pk)
    _check_plan_access(request.user, plan)
    if not request.user.profile.can_edit_plan(plan):
        raise PermissionDenied
    if request.method == 'POST':
        form = PlanHeaderForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            ip = AuditLogMiddleware.get_client_ip(request)
            log_action(request.user, 'UPDATE', 'AnnualPlan', plan, ip_address=ip)
            messages.success(request, 'تم تحديث رأس الخطة بنجاح.')
            return redirect('plans:detail', pk=plan.pk)
    else:
        form = PlanHeaderForm(instance=plan)
    return render(request, 'plans/plan_form.html', {
        'form': form, 'plan': plan, 'title': 'تعديل رأس الخطة'
    })


@login_required
@require_POST
def plan_submit(request, pk):
    plan = get_object_or_404(AnnualPlan, pk=pk)
    _check_plan_access(request.user, plan)
    if plan.status != AnnualPlan.STATUS_DRAFT:
        messages.error(request, 'لا يمكن تقديم الخطة في حالتها الحالية.')
        return redirect('plans:detail', pk=pk)
    if not request.user.profile.can_edit_plan(plan):
        raise PermissionDenied
    plan.submit(request.user)
    ip = AuditLogMiddleware.get_client_ip(request)
    log_action(request.user, 'UPDATE', 'AnnualPlan', plan,
               changes={'status': 'SUBMITTED'}, ip_address=ip)
    messages.success(request, 'تم تقديم الخطة للمراجعة بنجاح.')
    return redirect('plans:detail', pk=pk)


@login_required
@require_POST
def plan_approve(request, pk):
    plan = get_object_or_404(AnnualPlan, pk=pk)
    if not request.user.profile.can_review_plan(plan):
        raise PermissionDenied
    form = WorkflowCommentForm(request.POST)
    if form.is_valid():
        plan.approve(request.user, comment=form.cleaned_data.get('comment', ''))
        ip = AuditLogMiddleware.get_client_ip(request)
        log_action(request.user, 'UPDATE', 'AnnualPlan', plan,
                   changes={'status': 'APPROVED'}, ip_address=ip)
        messages.success(request, 'تم اعتماد الخطة بنجاح.')
    return redirect('plans:detail', pk=pk)


@login_required
@require_POST
def plan_reject(request, pk):
    plan = get_object_or_404(AnnualPlan, pk=pk)
    if not request.user.profile.can_review_plan(plan):
        raise PermissionDenied
    form = WorkflowCommentForm(request.POST)
    if form.is_valid():
        comment = form.cleaned_data.get('comment', '')
        if not comment:
            messages.error(request, 'يجب إدخال سبب الرفض.')
            return redirect('plans:detail', pk=pk)
        plan.reject(request.user, comment=comment)
        ip = AuditLogMiddleware.get_client_ip(request)
        log_action(request.user, 'UPDATE', 'AnnualPlan', plan,
                   changes={'status': 'REJECTED'}, ip_address=ip)
        messages.warning(request, 'تم رفض الخطة.')
    return redirect('plans:detail', pk=pk)


def _check_plan_access(user, plan):
    """Raise PermissionDenied if user has no access to this plan."""
    profile = user.profile
    if profile.is_admin():
        return
    if profile.is_reviewer():
        return
    if profile.formation is None:
        raise PermissionDenied
    formation = profile.formation
    allowed_ids = [formation.id] if formation else []
    if plan.formation_id not in allowed_ids:
        raise PermissionDenied
