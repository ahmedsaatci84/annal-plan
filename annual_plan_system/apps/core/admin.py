from django.contrib import admin
from .models import LookupValue, AuditLog


class AdminOnlyMixin:
    """Restricts all access to admin-role users only."""
    def _profile(self, request):
        try:
            return request.user.profile
        except Exception:
            return None

    def has_module_perms(self, request, app_label):  # noqa: used by Django admin
        profile = self._profile(request)
        return bool(profile and profile.is_admin())

    def has_view_permission(self, request, obj=None):
        profile = self._profile(request)
        return bool(profile and profile.is_admin())

    def has_add_permission(self, request):
        profile = self._profile(request)
        return bool(profile and profile.is_admin())

    def has_change_permission(self, request, obj=None):
        profile = self._profile(request)
        return bool(profile and profile.is_admin())

    def has_delete_permission(self, request, obj=None):
        profile = self._profile(request)
        return bool(profile and profile.is_admin())


@admin.register(LookupValue)
class LookupValueAdmin(AdminOnlyMixin, admin.ModelAdmin):
    list_display = ('category', 'code', 'label_ar', 'sort_order', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('label_ar', 'code')
    ordering = ('category', 'sort_order')


@admin.register(AuditLog)
class AuditLogAdmin(AdminOnlyMixin, admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'ip_address', 'created_at')
    list_filter = ('action', 'model_name')
    search_fields = ('user__username', 'object_repr')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'object_repr',
                       'changes_json', 'ip_address', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

