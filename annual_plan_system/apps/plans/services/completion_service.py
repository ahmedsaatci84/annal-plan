def compute_plan_summary(plan):
    """
    Returns a list of goal summaries with activity breakdown.
    """
    goals_data = []
    total_plan_activities = 0
    total_plan_completed = 0

    for goal in plan.goals.prefetch_related('activities').order_by('sequence'):
        activities = list(goal.activities.all())
        total = len(activities)
        completed = sum(1 for a in activities if a.activity_status == 'COMPLETED')
        in_progress = sum(1 for a in activities if a.activity_status == 'IN_PROGRESS')
        rolled_over = sum(1 for a in activities if a.activity_status == 'ROLLED_OVER')
        not_completed = sum(1 for a in activities if a.activity_status == 'NOT_STARTED')
        delayed = sum(1 for a in activities if a.activity_status == 'DELAYED')

        completion_pct = round((completed / total) * 100) if total else 0

        if completion_pct == 100:
            status = 'مكتمل'
            status_class = 'success'
        elif completion_pct > 0:
            status = 'قيد الإنجاز'
            status_class = 'warning'
            if delayed:
                status = 'متأخر'
                status_class = 'danger'
        else:
            status = 'لم يبدأ'
            status_class = 'secondary'
            if delayed:
                status = 'متأخر'
                status_class = 'danger'

        goals_data.append({
            'goal': goal,
            'total': total,
            'completed': completed,
            'in_progress': in_progress,
            'rolled_over': rolled_over,
            'not_completed': not_completed,
            'delayed': delayed,
            'completion_pct': completion_pct,
            'status': status,
            'status_class': status_class,
        })

        total_plan_activities += total
        total_plan_completed += completed

    overall_pct = (
        round((total_plan_completed / total_plan_activities) * 100)
        if total_plan_activities else 0
    )

    return {
        'goals': goals_data,
        'total_activities': total_plan_activities,
        'total_completed': total_plan_completed,
        'overall_pct': overall_pct,
    }
