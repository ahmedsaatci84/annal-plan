from apps.plans.models import AnnualPlan


def build_plan_analysis_context(plan):
    goals = plan.goals.prefetch_related('activities').all().order_by('sequence')
    risks = plan.risks.all().order_by('probability', 'id')

    goals_payload = []
    for goal in goals:
        activities = []
        for activity in goal.activities.all().order_by('sequence'):
            activities.append({
                'code': activity.code,
                'title': activity.title,
                'status': activity.activity_status,
                'planned_completion_pct': activity.planned_completion_pct,
                'actual_completion_pct': activity.actual_completion_pct,
                'start_date': str(activity.start_date),
                'end_date': str(activity.end_date),
            })

        goals_payload.append({
            'code': goal.code,
            'title': goal.title,
            'kpi_type': goal.kpi_type,
            'goal_type': goal.goal_type,
            'completion_pct': goal.completion_pct(),
            'status_label': goal.status_label(),
            'activities': activities,
        })

    risks_payload = [
        {
            'description': risk.risk_description,
            'probability': risk.probability,
            'impact': risk.impact_description,
            'treatment_plan': risk.treatment_plan,
        }
        for risk in risks
    ]

    return {
        'plan_meta': {
            'id': plan.id,
            'formation': plan.formation.name_ar,
            'year': plan.plan_year,
            'status': plan.status,
            'manager_name': plan.manager_name,
            'organizer_name': plan.organizer_name,
            'recommendations': plan.recommendations or '',
        },
        'goals': goals_payload,
        'risks': risks_payload,
    }


def get_accessible_plans_for_user(user):
    profile = user.profile
    if profile.is_admin():
        return AnnualPlan.objects.select_related('formation').order_by('-plan_year', 'formation__name_ar')
    if profile.is_reviewer():
        return AnnualPlan.objects.select_related('formation').order_by('-plan_year', 'formation__name_ar')
    if not profile.formation_id:
        return AnnualPlan.objects.none()
    return AnnualPlan.objects.filter(formation_id=profile.formation_id).select_related('formation').order_by('-plan_year')
