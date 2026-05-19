from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from apps.plans.models import AnnualPlan
from apps.plans.forms import SwotForm, RecommendationsForm
from apps.core.middleware import log_action, AuditLogMiddleware
from .plan_views import _check_plan_access
from django.core.exceptions import PermissionDenied


@login_required
def swot_edit(request, plan_pk):
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    _check_plan_access(request.user, plan)
    if not request.user.profile.can_edit_plan(plan):
        raise PermissionDenied
    swot = plan.swot if hasattr(plan, 'swot') else None
    if not swot:
        from apps.plans.models import SwotAnalysis
        swot, _ = SwotAnalysis.objects.get_or_create(plan=plan)
    if request.method == 'POST':
        form = SwotForm(request.POST, instance=swot)
        if form.is_valid():
            form.save()
            ip = AuditLogMiddleware.get_client_ip(request)
            log_action(request.user, 'UPDATE', 'SwotAnalysis', swot, ip_address=ip)
            messages.success(request, 'تم حفظ تحليل SWOT بنجاح.')
            return redirect('plans:detail', pk=plan.pk)
    else:
        form = SwotForm(instance=swot)
    return render(request, 'plans/sections/swot.html', {
        'form': form, 'plan': plan, 'swot': swot
    })


@login_required
def recommendations_edit(request, plan_pk):
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    _check_plan_access(request.user, plan)
    if plan.status not in ('DRAFT', 'REJECTED', 'UNDER_REVIEW'):
        raise PermissionDenied
    if not request.user.profile.can_edit_plan(plan) and not request.user.profile.is_reviewer():
        raise PermissionDenied
    if request.method == 'POST':
        form = RecommendationsForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ التوصيات بنجاح.')
            return redirect('plans:detail', pk=plan.pk)
    else:
        form = RecommendationsForm(instance=plan)
    return render(request, 'plans/sections/recommendations.html', {
        'form': form, 'plan': plan
    })


@login_required
def gantt_view(request, plan_pk):
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    _check_plan_access(request.user, plan)
    goals = plan.goals.prefetch_related('activities').order_by('sequence')
    return render(request, 'plans/sections/gantt.html', {
        'plan': plan, 'goals': goals
    })


@login_required
def gantt_data_api(request, plan_pk):
    """JSON API: returns gantt data for Chart.js."""
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    _check_plan_access(request.user, plan)
    from apps.plans.services.gantt_service import build_gantt_data
    return JsonResponse(build_gantt_data(plan))


@login_required
def summary_view(request, plan_pk):
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    _check_plan_access(request.user, plan)
    from apps.plans.services.completion_service import compute_plan_summary
    summary = compute_plan_summary(plan)
    return render(request, 'plans/sections/summary.html', {
        'plan': plan, 'summary': summary
    })


@login_required
def summary_api(request, plan_pk):
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    _check_plan_access(request.user, plan)
    from apps.plans.services.completion_service import compute_plan_summary
    return JsonResponse(compute_plan_summary(plan))


@login_required
def plan_export_pdf(request, plan_pk):
    plan = get_object_or_404(AnnualPlan, pk=plan_pk)
    _check_plan_access(request.user, plan)
    from apps.plans.services.pdf_service import export_plan_pdf
    return export_plan_pdf(request, plan)
