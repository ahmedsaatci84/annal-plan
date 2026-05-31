from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Avg, Q

from apps.plans.models import AnnualPlan, Activity
from apps.plans.services.completion_service import compute_plan_summary


@login_required
def dashboard_index(request):
    profile = request.user.profile
    current_year = timezone.now().year

    if profile.is_admin():
        return _admin_dashboard(request, current_year)
    elif profile.is_manager():
        return _manager_dashboard(request, current_year)
    else:
        return _user_dashboard(request, current_year)


def _admin_dashboard(request, year):
    plans = AnnualPlan.objects.filter(plan_year=year).select_related('formation')
    total_plans = plans.count()
    status_counts = {
        s: plans.filter(status=s).count()
        for s, _ in AnnualPlan.STATUS_CHOICES
    }
    recent_plans = plans.order_by('-updated_at')[:10]

    # Risk distribution
    from apps.plans.models import Risk
    risk_counts = {
        'LOW': Risk.objects.filter(plan__plan_year=year, probability='LOW').count(),
        'MEDIUM': Risk.objects.filter(plan__plan_year=year, probability='MEDIUM').count(),
        'HIGH': Risk.objects.filter(plan__plan_year=year, probability='HIGH').count(),
    }

    return render(request, 'dashboard/admin_dashboard.html', {
        'year': year,
        'total_plans': total_plans,
        'status_counts': status_counts,
        'recent_plans': recent_plans,
        'risk_counts': risk_counts,
    })


def _manager_dashboard(request, year):
    profile = request.user.profile
    formation = profile.formation
    if not formation:
        return render(request, 'dashboard/no_formation.html', {})

    descendants = []
    ids = [formation.id]
    plans = AnnualPlan.objects.filter(
        plan_year=year, formation_id__in=ids
    ).select_related('formation')

    overdue_activities = Activity.objects.filter(
        goal__plan__formation_id__in=ids,
        goal__plan__plan_year=year,
        end_date__lt=timezone.now().date(),
        activity_status__in=['NOT_STARTED', 'IN_PROGRESS'],
    ).count()

    return render(request, 'dashboard/manager_dashboard.html', {
        'year': year,
        'plans': plans,
        'overdue_activities': overdue_activities,
        'formation': formation,
    })


def _user_dashboard(request, year):
    profile = request.user.profile
    formation = profile.formation
    if not formation:
        return render(request, 'dashboard/no_formation.html', {})

    plans = AnnualPlan.objects.filter(
        plan_year=year, formation=formation
    ).select_related('formation')

    return render(request, 'dashboard/user_dashboard.html', {
        'year': year,
        'plans': plans,
        'formation': formation,
    })
