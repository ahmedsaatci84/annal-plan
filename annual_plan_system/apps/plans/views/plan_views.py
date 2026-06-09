from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied, ValidationError
from django.views.decorators.http import require_POST

from apps.core.middleware import log_action, AuditLogMiddleware
from apps.plans.models import AnnualPlan, SwotAnalysis
from apps.plans.forms import PlanHeaderForm, WorkflowCommentForm, PlanStatusUpdateForm
from apps.plans.services.status_transition_service import (
    apply_status_transition,
    get_allowed_target_statuses,
)


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
        'plan_data': [
            (plan, profile.can_edit_plan(plan), profile.can_review_plan(plan))
            for plan in plans
        ],
        'status_choices': AnnualPlan.STATUS_CHOICES,
        'selected_year': year_filter,
        'selected_status': status_filter,
        'is_admin': profile.is_admin(),
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

    profile = request.user.profile
    change_status_choices = get_allowed_target_statuses(plan, request.user)
    return render(request, 'plans/plan_detail.html', {
        'plan': plan,
        'swot': swot,
        'goals': goals,
        'risks': risks,
        'workflow_logs': workflow_logs,
        'can_edit': profile.can_edit_plan(plan),
        'can_review': profile.can_review_plan(plan),
        'is_admin': profile.is_admin(),
        'change_status_choices': change_status_choices,
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
def plan_delete(request, pk):
    plan = get_object_or_404(AnnualPlan, pk=pk)
    if not request.user.profile.is_admin():
        raise PermissionDenied

    ip = AuditLogMiddleware.get_client_ip(request)
    log_action(request.user, 'DELETE', 'AnnualPlan', plan, ip_address=ip)
    plan.delete()
    messages.success(request, 'تم حذف الخطة بنجاح.')
    return redirect('plans:list')


@login_required
@require_POST
def plan_change_status(request, pk):
    plan = get_object_or_404(AnnualPlan, pk=pk)
    _check_plan_access(request.user, plan)

    target_choices = get_allowed_target_statuses(plan, request.user)
    if not target_choices:
        raise PermissionDenied

    form = PlanStatusUpdateForm(request.POST, current_status=plan.status)
    form.fields['status'].choices = target_choices
    if not form.is_valid():
        messages.error(request, 'تعذر تحديث حالة الخطة. يرجى التحقق من البيانات المدخلة.')
        return redirect(request.POST.get('next') or 'plans:list')

    new_status = form.cleaned_data['status']
    comment = form.cleaned_data.get('comment', '').strip()
    old_status = plan.status

    try:
        apply_status_transition(plan, request.user, new_status, comment=comment)
    except ValidationError as exc:
        messages.error(request, exc.messages[0] if exc.messages else 'تعذر تحديث حالة الخطة.')
        return redirect(request.POST.get('next') or 'plans:list')
    except PermissionDenied:
        raise

    ip = AuditLogMiddleware.get_client_ip(request)
    log_action(
        request.user,
        'UPDATE',
        'AnnualPlan',
        plan,
        changes={'from_status': old_status, 'to_status': new_status, 'comment': comment or None},
        ip_address=ip,
    )
    messages.success(request, 'تم تحديث حالة الخطة بنجاح.')
    return redirect(request.POST.get('next') or 'plans:list')


@login_required
@require_POST
def plan_submit(request, pk):
    plan = get_object_or_404(AnnualPlan, pk=pk)
    _check_plan_access(request.user, plan)
    old_status = plan.status
    try:
        apply_status_transition(plan, request.user, AnnualPlan.STATUS_SUBMITTED)
    except ValidationError as exc:
        messages.error(request, exc.messages[0] if exc.messages else 'لا يمكن تقديم الخطة في حالتها الحالية.')
        return redirect('plans:detail', pk=pk)
    ip = AuditLogMiddleware.get_client_ip(request)
    log_action(request.user, 'UPDATE', 'AnnualPlan', plan,
               changes={'from_status': old_status, 'to_status': AnnualPlan.STATUS_SUBMITTED}, ip_address=ip)
    messages.success(request, 'تم تقديم الخطة للمراجعة بنجاح.')
    return redirect('plans:detail', pk=pk)


@login_required
@require_POST
def plan_approve(request, pk):
    plan = get_object_or_404(AnnualPlan, pk=pk)
    form = WorkflowCommentForm(request.POST)
    if form.is_valid():
        old_status = plan.status
        comment = form.cleaned_data.get('comment', '')
        try:
            apply_status_transition(plan, request.user, AnnualPlan.STATUS_APPROVED, comment=comment)
        except ValidationError as exc:
            messages.error(request, exc.messages[0] if exc.messages else 'تعذر اعتماد الخطة.')
            return redirect('plans:detail', pk=pk)
        ip = AuditLogMiddleware.get_client_ip(request)
        log_action(request.user, 'UPDATE', 'AnnualPlan', plan,
                   changes={'from_status': old_status, 'to_status': AnnualPlan.STATUS_APPROVED}, ip_address=ip)
        messages.success(request, 'تم اعتماد الخطة بنجاح.')
    return redirect('plans:detail', pk=pk)


@login_required
@require_POST
def plan_reject(request, pk):
    plan = get_object_or_404(AnnualPlan, pk=pk)
    form = WorkflowCommentForm(request.POST)
    if form.is_valid():
        comment = form.cleaned_data.get('comment', '')
        old_status = plan.status
        try:
            apply_status_transition(plan, request.user, AnnualPlan.STATUS_REJECTED, comment=comment)
        except ValidationError as exc:
            messages.error(request, exc.messages[0] if exc.messages else 'يجب إدخال سبب الرفض.')
            return redirect('plans:detail', pk=pk)
        ip = AuditLogMiddleware.get_client_ip(request)
        log_action(request.user, 'UPDATE', 'AnnualPlan', plan,
                   changes={'from_status': old_status, 'to_status': AnnualPlan.STATUS_REJECTED}, ip_address=ip)
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


@login_required
@require_POST
def plan_start_review(request, pk):
    plan = get_object_or_404(AnnualPlan, pk=pk)
    old_status = plan.status
    try:
        apply_status_transition(plan, request.user, AnnualPlan.STATUS_UNDER_REVIEW)
    except ValidationError as exc:
        messages.error(request, exc.messages[0] if exc.messages else 'لا يمكن بدء المراجعة في الحالة الحالية للخطة.')
        return redirect('plans:detail', pk=pk)
    ip = AuditLogMiddleware.get_client_ip(request)
    log_action(request.user, 'UPDATE', 'AnnualPlan', plan,
               changes={'from_status': old_status, 'to_status': AnnualPlan.STATUS_UNDER_REVIEW}, ip_address=ip)
    messages.info(request, 'تم بدء مراجعة الخطة.')
    return redirect('plans:detail', pk=pk)


@login_required
@require_POST
def plan_reopen(request, pk):
    plan = get_object_or_404(AnnualPlan, pk=pk)
    _check_plan_access(request.user, plan)
    old_status = plan.status
    try:
        apply_status_transition(plan, request.user, AnnualPlan.STATUS_DRAFT)
    except ValidationError as exc:
        messages.error(request, exc.messages[0] if exc.messages else 'يمكن إعادة فتح الخطط المرفوضة فقط.')
        return redirect('plans:detail', pk=pk)
    ip = AuditLogMiddleware.get_client_ip(request)
    log_action(request.user, 'UPDATE', 'AnnualPlan', plan,
               changes={'from_status': old_status, 'to_status': AnnualPlan.STATUS_DRAFT}, ip_address=ip)
    messages.success(request, 'تمت إعادة فتح الخطة للتعديل.')
    return redirect('plans:detail', pk=pk)


@login_required
@require_POST
def plan_archive(request, pk):
    plan = get_object_or_404(AnnualPlan, pk=pk)
    old_status = plan.status
    try:
        apply_status_transition(plan, request.user, AnnualPlan.STATUS_ARCHIVED)
    except ValidationError as exc:
        messages.error(request, exc.messages[0] if exc.messages else 'يمكن أرشفة الخطط المعتمدة فقط.')
        return redirect('plans:detail', pk=pk)
    ip = AuditLogMiddleware.get_client_ip(request)
    log_action(request.user, 'UPDATE', 'AnnualPlan', plan,
               changes={'from_status': old_status, 'to_status': AnnualPlan.STATUS_ARCHIVED}, ip_address=ip)
    messages.success(request, 'تم أرشفة الخطة بنجاح.')
    return redirect('plans:detail', pk=pk)
