from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin that enforces role-based access on top of login requirement.
    Set `allowed_roles` as a list/tuple on the view class.
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not hasattr(request.user, 'profile'):
            raise PermissionDenied
        role = request.user.profile.role
        if self.allowed_roles and role not in self.allowed_roles:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['ADMIN']


class ManagerOrAdminMixin(RoleRequiredMixin):
    allowed_roles = ['ADMIN', 'MANAGER']


class ReviewerMixin(RoleRequiredMixin):
    allowed_roles = ['ADMIN', 'MANAGER', 'REVIEWER']
