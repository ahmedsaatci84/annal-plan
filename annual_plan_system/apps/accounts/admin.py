from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile


def _get_profile(request):
    try:
        return request.user.profile
    except Exception:
        return None


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'ملف المستخدم'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        profile = _get_profile(request)
        if profile is None or profile.is_admin():
            return qs
        # Non-admin users see only the user linked to their formation
        if profile.formation:
            return qs.filter(profile__formation=profile.formation)
        return qs.none()

    def has_add_permission(self, request):
        profile = _get_profile(request)
        return bool(profile and profile.is_admin())

    def has_change_permission(self, request, obj=None):
        profile = _get_profile(request)
        return bool(profile and profile.is_admin())

    def has_delete_permission(self, request, obj=None):
        profile = _get_profile(request)
        return bool(profile and profile.is_admin())


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
