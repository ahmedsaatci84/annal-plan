from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AnnualPlan(models.Model):
    STATUS_DRAFT = 'DRAFT'
    STATUS_SUBMITTED = 'SUBMITTED'
    STATUS_UNDER_REVIEW = 'UNDER_REVIEW'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_ARCHIVED = 'ARCHIVED'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'مسودة'),
        (STATUS_SUBMITTED, 'مقدمة'),
        (STATUS_UNDER_REVIEW, 'قيد المراجعة'),
        (STATUS_APPROVED, 'معتمدة'),
        (STATUS_REJECTED, 'مرفوضة'),
        (STATUS_ARCHIVED, 'مؤرشفة'),
    ]

    formation = models.ForeignKey(
        'formations.Formation', on_delete=models.PROTECT,
        related_name='annual_plans', verbose_name='التشكيل'
    )
    plan_year = models.PositiveSmallIntegerField(verbose_name='سنة الخطة')
    manager_name = models.CharField(max_length=200, verbose_name='اسم مدير التشكيل')
    organizer_name = models.CharField(max_length=200, verbose_name='اسم منظم الاستمارة')
    endorsement_text = models.TextField(blank=True, null=True, verbose_name='نص المصادقة')
    endorsement_date = models.DateField(blank=True, null=True, verbose_name='تاريخ المصادقة')
    endorsement_ref_no = models.CharField(
        max_length=50, blank=True, null=True, verbose_name='رقم الإشارة'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT, verbose_name='الحالة'
    )
    recommendations = models.TextField(
        blank=True, null=True, verbose_name='سابعاً – التوصيات النهائية'
    )
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='created_plans', verbose_name='أنشأ بواسطة'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التعديل')
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ التقديم')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الاعتماد')

    class Meta:
        unique_together = ('formation', 'plan_year')
        verbose_name = 'خطة سنوية'
        verbose_name_plural = 'الخطط السنوية'
        ordering = ['-plan_year', 'formation__name_ar']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['plan_year']),
        ]

    def __str__(self):
        return f'خطة {self.formation.name_ar} — {self.plan_year}'

    def is_editable(self):
        return self.status in (self.STATUS_DRAFT, self.STATUS_REJECTED)

    def is_locked(self):
        return self.status == self.STATUS_APPROVED

    def submit(self, user):
        from apps.plans.models.workflow import PlanWorkflowLog
        old = self.status
        self.status = self.STATUS_SUBMITTED
        self.submitted_at = timezone.now()
        self.save(update_fields=['status', 'submitted_at'])
        PlanWorkflowLog.objects.create(
            plan=self, from_status=old, to_status=self.STATUS_SUBMITTED, performed_by=user
        )

    def approve(self, user, comment=''):
        from apps.plans.models.workflow import PlanWorkflowLog
        old = self.status
        self.status = self.STATUS_APPROVED
        self.approved_at = timezone.now()
        self.save(update_fields=['status', 'approved_at'])
        PlanWorkflowLog.objects.create(
            plan=self, from_status=old, to_status=self.STATUS_APPROVED,
            performed_by=user, comment=comment
        )

    def reject(self, user, comment):
        from apps.plans.models.workflow import PlanWorkflowLog
        old = self.status
        self.status = self.STATUS_REJECTED
        self.save(update_fields=['status'])
        PlanWorkflowLog.objects.create(
            plan=self, from_status=old, to_status=self.STATUS_REJECTED,
            performed_by=user, comment=comment
        )
