from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from apps.plans.models import AnnualPlan, PlanWorkflowLog


REVIEW_FLOW_TRANSITIONS = {
    AnnualPlan.STATUS_SUBMITTED: {
        AnnualPlan.STATUS_UNDER_REVIEW,
        AnnualPlan.STATUS_APPROVED,
        AnnualPlan.STATUS_REJECTED,
    },
    AnnualPlan.STATUS_UNDER_REVIEW: {
        AnnualPlan.STATUS_APPROVED,
        AnnualPlan.STATUS_REJECTED,
    },
}

EDITOR_FLOW_TRANSITIONS = {
    AnnualPlan.STATUS_DRAFT: {AnnualPlan.STATUS_SUBMITTED},
    AnnualPlan.STATUS_REJECTED: {AnnualPlan.STATUS_DRAFT},
}


class StatusTransitionError(ValidationError):
    """Raised when plan status transition cannot be applied."""


def requires_comment(from_status, to_status):
    """Return True when workflow comment must be provided."""
    if to_status == AnnualPlan.STATUS_REJECTED:
        return True
    if (
        from_status == AnnualPlan.STATUS_APPROVED
        and to_status in (
            AnnualPlan.STATUS_DRAFT,
            AnnualPlan.STATUS_SUBMITTED,
            AnnualPlan.STATUS_UNDER_REVIEW,
            AnnualPlan.STATUS_REJECTED,
        )
    ):
        return True
    return False


def _is_valid_status(status):
    valid_statuses = {value for value, _ in AnnualPlan.STATUS_CHOICES}
    return status in valid_statuses


def can_user_transition_status(plan, user, to_status):
    """Check if current user can move plan from current status to to_status."""
    if not _is_valid_status(to_status):
        return False
    from_status = plan.status
    if from_status == to_status:
        return False

    profile = user.profile
    if profile.is_admin():
        return True

    review_targets = REVIEW_FLOW_TRANSITIONS.get(from_status, set())
    if to_status in review_targets and profile.can_review_plan(plan):
        return True

    editor_targets = EDITOR_FLOW_TRANSITIONS.get(from_status, set())
    if to_status in editor_targets and profile.can_edit_plan(plan):
        return True

    return False


def get_allowed_target_statuses(plan, user):
    """Return filtered status choices the user can transition the plan to."""
    return [
        (value, label)
        for value, label in AnnualPlan.STATUS_CHOICES
        if can_user_transition_status(plan, user, value)
    ]


def apply_status_transition(plan, user, to_status, comment=''):
    """Apply status transition with validation, timestamps, and workflow log."""
    comment = (comment or '').strip()
    from_status = plan.status

    if not _is_valid_status(to_status):
        raise StatusTransitionError('الحالة المختارة غير صالحة.')

    if from_status == to_status:
        raise StatusTransitionError('الحالة الحالية مطابقة للحالة المختارة.')

    if not can_user_transition_status(plan, user, to_status):
        raise PermissionDenied

    if requires_comment(from_status, to_status) and not comment:
        raise StatusTransitionError('يرجى إدخال سبب/تعليق لهذا التحويل.')

    update_fields = ['status']
    current_time = timezone.now()

    plan.status = to_status

    if to_status == AnnualPlan.STATUS_DRAFT:
        if plan.submitted_at is not None:
            plan.submitted_at = None
            update_fields.append('submitted_at')
        if plan.approved_at is not None:
            plan.approved_at = None
            update_fields.append('approved_at')
    else:
        if to_status in (
            AnnualPlan.STATUS_SUBMITTED,
            AnnualPlan.STATUS_UNDER_REVIEW,
            AnnualPlan.STATUS_APPROVED,
        ) and plan.submitted_at is None:
            plan.submitted_at = current_time
            update_fields.append('submitted_at')

        if to_status == AnnualPlan.STATUS_APPROVED:
            plan.approved_at = current_time
            update_fields.append('approved_at')
        elif to_status != AnnualPlan.STATUS_ARCHIVED and plan.approved_at is not None:
            plan.approved_at = None
            update_fields.append('approved_at')

    plan.save(update_fields=update_fields)
    PlanWorkflowLog.objects.create(
        plan=plan,
        from_status=from_status,
        to_status=to_status,
        performed_by=user,
        comment=comment,
    )

    return plan
