from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_ADMIN = 'ADMIN'
    ROLE_MANAGER = 'MANAGER'
    ROLE_ORGANIZER = 'ORGANIZER'
    ROLE_REVIEWER = 'REVIEWER'
    ROLE_VIEWER = 'VIEWER'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'مسؤول النظام'),
        (ROLE_MANAGER, 'مدير التشكيل'),
        (ROLE_ORGANIZER, 'منظم الاستمارة'),
        (ROLE_REVIEWER, 'مراجع'),
        (ROLE_VIEWER, 'مشاهد'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='profile', verbose_name='المستخدم'
    )
    formation = models.ForeignKey(
        'formations.Formation', on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='members', verbose_name='التشكيل'
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default=ROLE_ORGANIZER,
        verbose_name='الدور'
    )
    full_name_ar = models.CharField(max_length=200, verbose_name='الاسم الكامل بالعربية')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        verbose_name = 'ملف مستخدم'
        verbose_name_plural = 'ملفات المستخدمين'
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
