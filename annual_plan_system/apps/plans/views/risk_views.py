from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST

from apps.core.middleware import log_action, AuditLogMiddleware
from apps.plans.models import AnnualPlan, Risk
from apps.plans.forms import RiskForm
from .plan_views import _check_plan_access


@login_required
def risk_create(request, plan_pk):
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    _check_plan_access(request.user, plan)
    if not request.user.profile.can_edit_plan(plan):
        raise PermissionDenied
    if request.method == 'POST':
        form = RiskForm(request.POST)
        if form.is_valid():
            risk = form.save(commit=False)
            risk.plan = plan
            risk.save()
            ip = AuditLogMiddleware.get_client_ip(request)
            log_action(request.user, 'CREATE', 'Risk', risk, ip_address=ip)
            messages.success(request, 'تم إضافة المخاطرة بنجاح.')
            return redirect('plans:detail', pk=plan.pk)
    else:
        form = RiskForm()
    return render(request, 'plans/risk_form.html', {
        'form': form, 'plan': plan, 'title': 'إضافة مخاطرة'
    })


@login_required
def risk_edit(request, plan_pk, risk_pk):
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    risk = get_object_or_404(Risk, pk=risk_pk, plan=plan)
    _check_plan_access(request.user, plan)
    if not request.user.profile.can_edit_plan(plan):
        raise PermissionDenied
    if request.method == 'POST':
        form = RiskForm(request.POST, instance=risk)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المخاطرة بنجاح.')
            return redirect('plans:detail', pk=plan.pk)
    else:
        form = RiskForm(instance=risk)
    return render(request, 'plans/risk_form.html', {
        'form': form, 'plan': plan, 'risk': risk, 'title': 'تعديل مخاطرة'
    })


@login_required
@require_POST
def risk_delete(request, plan_pk, risk_pk):
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    risk = get_object_or_404(Risk, pk=risk_pk, plan=plan)
    _check_plan_access(request.user, plan)
    if not request.user.profile.can_edit_plan(plan):
        raise PermissionDenied
    ip = AuditLogMiddleware.get_client_ip(request)
    log_action(request.user, 'DELETE', 'Risk', risk, ip_address=ip)
    risk.delete()
    messages.success(request, 'تم حذف المخاطرة بنجاح.')
    return redirect('plans:detail', pk=plan.pk)
