from django.contrib import admin
from .models import LookupValue, AuditLog


@admin.register(LookupValue)
class LookupValueAdmin(admin.ModelAdmin):
    list_display = ('category', 'code', 'label_ar', 'sort_order', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('label_ar', 'code')
    ordering = ('category', 'sort_order')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'ip_address', 'created_at')
    list_filter = ('action', 'model_name')
    search_fields = ('user__username', 'object_repr')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'object_repr',
                       'changes_json', 'ip_address', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
