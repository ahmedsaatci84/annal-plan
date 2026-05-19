from .plan_views import (
    plan_list, plan_create, plan_detail, plan_edit,
    plan_submit, plan_approve, plan_reject,
)
from .goal_views import goal_list, goal_create, goal_edit, goal_delete
from .activity_views import (
    activity_create, activity_edit, activity_update_progress, activity_delete
)
from .risk_views import risk_create, risk_edit, risk_delete
from .misc_views import (
    swot_edit, recommendations_edit, gantt_view, gantt_data_api,
    summary_view, summary_api, plan_export_pdf,
)

__all__ = [
    'plan_list', 'plan_create', 'plan_detail', 'plan_edit',
    'plan_submit', 'plan_approve', 'plan_reject',
    'goal_list', 'goal_create', 'goal_edit', 'goal_delete',
    'activity_create', 'activity_edit', 'activity_update_progress', 'activity_delete',
    'risk_create', 'risk_edit', 'risk_delete',
    'swot_edit', 'recommendations_edit', 'gantt_view', 'gantt_data_api',
    'summary_view', 'summary_api', 'plan_export_pdf',
]
