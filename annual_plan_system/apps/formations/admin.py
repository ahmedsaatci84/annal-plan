from django.contrib import admin
from .models import Formation


class FormationScopedAdminMixin:
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
            return qs.filter(pk=profile.formation.pk)
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


@admin.register(Formation)
class FormationAdmin(FormationScopedAdminMixin, admin.ModelAdmin):
    list_display = ('code', 'name_ar', 'level', 'parent', 'is_active')
    list_filter = ('level', 'is_active')
    search_fields = ('name_ar', 'code')
    ordering = ('level', 'name_ar')
