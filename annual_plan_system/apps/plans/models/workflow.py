from django.db import models
from django.contrib.auth.models import User


class PlanWorkflowLog(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'مسودة'),
        ('SUBMITTED', 'مقدمة'),
        ('UNDER_REVIEW', 'قيد المراجعة'),
        ('APPROVED', 'معتمدة'),
        ('REJECTED', 'مرفوضة'),
        ('ARCHIVED', 'مؤرشفة'),
    ]

    plan = models.ForeignKey(
        'plans.AnnualPlan', on_delete=models.CASCADE,
        related_name='workflow_logs', verbose_name='الخطة'
    )
    from_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, null=True, blank=True,
        verbose_name='الحالة السابقة'
    )
    to_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        verbose_name='الحالة الجديدة'
    )
    performed_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='workflow_actions', verbose_name='نفّذ بواسطة'
    )
    comment = models.TextField(blank=True, null=True, verbose_name='التعليق')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإجراء')

    class Meta:
        verbose_name = 'سجل سير العمل'
        verbose_name_plural = 'سجلات سير العمل'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['plan']),
        ]

    def __str__(self):
        return (
            f'{self.plan} | {self.from_status} → {self.to_status} '
            f'| {self.performed_by} | {self.created_at:%Y-%m-%d %H:%M}'
        )
