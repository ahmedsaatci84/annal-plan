from django.contrib import admin
from apps.plans.models import AnnualPlan, Goal, Activity, Risk, PlanWorkflowLog, SwotAnalysis


# ---------------------------------------------------------------------------
# Base mixin — restricts queryset and write-access to admin role users only
# ---------------------------------------------------------------------------
class FormationScopedAdminMixin:
    """
    Non-admin users see only data that belongs to their formation.
    Admin-role users see everything and can add / change / delete freely.
    """
    # Each subclass sets this to the ORM lookup path to `formations.Formation`,
    # e.g. 'formation', 'plan__formation', 'goal__plan__formation', etc.
    formation_lookup = 'formation'

    def _profile(self, request):
        try:
            return request.user.profile
        except Exception:
            return None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        profile = self._profile(request)
        if profile is None or profile.is_admin():
            return qs
        if profile.formation:
            return qs.filter(**{self.formation_lookup: profile.formation})
        return qs.none()

    def has_add_permission(self, request):
        profile = self._profile(request)
        return bool(profile and profile.is_admin())

    def has_change_permission(self, request, obj=None):
        profile = self._profile(request)
        return bool(profile and profile.is_admin())

    def has_delete_permission(self, request, obj=None):
        profile = self._profile(request)
        return bool(profile and profile.is_admin())


# ---------------------------------------------------------------------------
# Inlines
# ---------------------------------------------------------------------------
class GoalInline(admin.TabularInline):
    model = Goal
    extra = 0
    fields = ('sequence', 'code', 'title', 'kpi_type', 'goal_type')
    readonly_fields = ('code',)


# ---------------------------------------------------------------------------
# ModelAdmin registrations
# ---------------------------------------------------------------------------
@admin.register(AnnualPlan)
class AnnualPlanAdmin(FormationScopedAdminMixin, admin.ModelAdmin):
    formation_lookup = 'formation'
    list_display = ('formation', 'plan_year', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'plan_year')
    search_fields = ('formation__name_ar', 'manager_name')
    inlines = [GoalInline]
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'submitted_at', 'approved_at')


@admin.register(Goal)
class GoalAdmin(FormationScopedAdminMixin, admin.ModelAdmin):
    formation_lookup = 'formation'
    list_display = ('code', 'title', 'kpi_type', 'goal_type', 'plan', 'formation')
    list_filter = ('goal_type', 'formation')
    search_fields = ('title',)


@admin.register(Activity)
class ActivityAdmin(FormationScopedAdminMixin, admin.ModelAdmin):
    formation_lookup = 'goal__plan__formation'
    list_display = ('code', 'title', 'activity_status', 'planned_completion_pct', 'actual_completion_pct')
    list_filter = ('activity_status',)


@admin.register(Risk)
class RiskAdmin(FormationScopedAdminMixin, admin.ModelAdmin):
    formation_lookup = 'formation'
    list_display = ('plan', 'formation', 'probability', 'risk_description')
    list_filter = ('probability', 'formation')


@admin.register(SwotAnalysis)
class SwotAnalysisAdmin(FormationScopedAdminMixin, admin.ModelAdmin):
    formation_lookup = 'plan__formation'
    list_display = ('plan',)


@admin.register(PlanWorkflowLog)
class PlanWorkflowLogAdmin(FormationScopedAdminMixin, admin.ModelAdmin):
    formation_lookup = 'plan__formation'
    list_display = ('plan', 'from_status', 'to_status', 'performed_by', 'created_at')
    readonly_fields = ('plan', 'from_status', 'to_status', 'performed_by', 'comment', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

