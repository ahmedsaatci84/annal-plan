from django.contrib import admin
from .models import Formation, ParentFormation


@admin.register(ParentFormation)
class ParentFormationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)


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
    list_display = ('name_ar', 'level', 'parent_formation', 'is_active')
    list_filter = ('level', 'is_active', 'parent_formation')
    search_fields = ('name_ar',)
    ordering = ('level', 'name_ar')
