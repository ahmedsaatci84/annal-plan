from django.contrib import admin
from apps.plans.models import AnnualPlan, Goal, Activity, Risk, PlanWorkflowLog, SwotAnalysis


class GoalInline(admin.TabularInline):
    model = Goal
    extra = 0
    fields = ('sequence', 'code', 'title', 'kpi_type', 'goal_type')
    readonly_fields = ('code',)


@admin.register(AnnualPlan)
class AnnualPlanAdmin(admin.ModelAdmin):
    list_display = ('formation', 'plan_year', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'plan_year')
    search_fields = ('formation__name_ar', 'manager_name')
    inlines = [GoalInline]
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'submitted_at', 'approved_at')


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'kpi_type', 'goal_type', 'plan')
    list_filter = ('goal_type',)
    search_fields = ('title',)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'activity_status', 'planned_completion_pct', 'actual_completion_pct')
    list_filter = ('activity_status',)


@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ('plan', 'probability', 'risk_description')
    list_filter = ('probability',)


@admin.register(PlanWorkflowLog)
class PlanWorkflowLogAdmin(admin.ModelAdmin):
    list_display = ('plan', 'from_status', 'to_status', 'performed_by', 'created_at')
    readonly_fields = ('plan', 'from_status', 'to_status', 'performed_by', 'comment', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
