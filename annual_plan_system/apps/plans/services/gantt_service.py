from datetime import date


MONTHS = [
    (1, 'كانون الثاني'),
    (2, 'شباط'),
    (3, 'آذار'),
    (4, 'نيسان'),
    (5, 'أيار'),
    (6, 'حزيران'),
    (7, 'تموز'),
    (8, 'آب'),
    (9, 'أيلول'),
    (10, 'تشرين الأول'),
    (11, 'تشرين الثاني'),
    (12, 'كانون الأول'),
]

STATUS_COLORS = {
    'NOT_STARTED': '#e9ecef',
    'IN_PROGRESS': '#ffc107',
    'COMPLETED': '#28a745',
    'DELAYED': '#dc3545',
    'ROLLED_OVER': '#fd7e14',
    'STOPPED': '#6c757d',
}


def _activity_covers_month(activity, year, month):
    """Returns True if the activity spans into the given month of the given year."""
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year, 12, 31)
    else:
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        month_end = date(year, month, last_day)
    return activity.start_date <= month_end and activity.end_date >= month_start


def build_gantt_data(plan):
    year = plan.plan_year
    rows = []

    for goal in plan.goals.prefetch_related('activities').order_by('sequence'):
        for activity in goal.activities.order_by('sequence'):
            months_active = []
            for month_num, month_name in MONTHS:
                months_active.append(_activity_covers_month(activity, year, month_num))

            rows.append({
                'goal_code': goal.code,
                'goal_title': str(goal.title)[:60],
                'activity_code': activity.code,
                'activity_title': str(activity.title)[:60],
                'start_date': str(activity.start_date),
                'end_date': str(activity.end_date),
                'status': activity.activity_status,
                'color': STATUS_COLORS.get(activity.activity_status, '#e9ecef'),
                'months_active': months_active,
            })

    return {
        'year': year,
        'months': [{'num': m, 'name': n} for m, n in MONTHS],
        'rows': rows,
    }
