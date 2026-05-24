from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    ROLE_ADMIN = 'ADMIN'
    ROLE_MANAGER = 'MANAGER'
    ROLE_ORGANIZER = 'ORGANIZER'
    ROLE_REVIEWER = 'REVIEWER'
    ROLE_VIEWER = 'VIEWER'

    ROLE_CHOICES = [
        (ROLE_ADMIN, _('System Admin')),
        (ROLE_MANAGER, _('Formation Manager')),
        (ROLE_ORGANIZER, _('Form Organizer')),
        (ROLE_REVIEWER, _('Reviewer')),
        (ROLE_VIEWER, _('Viewer')),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='profile', verbose_name=_('user')
    )
    formation = models.OneToOneField(
        'formations.Formation', on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='user_profile', verbose_name=_('formation')
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default=ROLE_ORGANIZER,
        verbose_name=_('Role')
    )
    full_name_ar = models.CharField(max_length=200, verbose_name=_('full name in arabic'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
        indexes = [
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f'{self.full_name_ar} ({self.get_role_display()})'

    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    def is_manager(self):
        return self.role == self.ROLE_MANAGER

    def is_organizer(self):
        return self.role == self.ROLE_ORGANIZER

    def is_reviewer(self):
        return self.role == self.ROLE_REVIEWER

    def can_edit_plan(self, plan):
        """Check if this user can edit a given plan."""
        if self.role == self.ROLE_ADMIN:
            return True
        if plan.status not in ('DRAFT', 'REJECTED'):
            return False
        if self.role in (self.ROLE_MANAGER, self.ROLE_ORGANIZER):
            return plan.formation_id == self.formation_id
        return False

    def can_review_plan(self, plan):
        if self.role == self.ROLE_ADMIN:
            return True
        if self.role in (self.ROLE_MANAGER, self.ROLE_REVIEWER):
            return plan.status in ('SUBMITTED', 'UNDER_REVIEW')
        return False
