from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class AnnualPlan(models.Model):
    STATUS_DRAFT = 'DRAFT'
    STATUS_SUBMITTED = 'SUBMITTED'
    STATUS_UNDER_REVIEW = 'UNDER_REVIEW'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_ARCHIVED = 'ARCHIVED'

    STATUS_CHOICES = [
        (STATUS_DRAFT, _('Draft')),
        (STATUS_SUBMITTED, _('Submitted')),
        (STATUS_UNDER_REVIEW, _('Under Review')),
        (STATUS_APPROVED, _('Approved')),
        (STATUS_REJECTED, _('Rejected')),
        (STATUS_ARCHIVED, _('Archived')),
    ]

    formation = models.ForeignKey(
        'formations.Formation', on_delete=models.PROTECT,
        related_name='annual_plans', verbose_name=_('formation')
    )
    plan_year = models.PositiveSmallIntegerField(verbose_name=_('plan year'))
    manager_name = models.CharField(max_length=200, verbose_name=_('manager name'))
    organizer_name = models.CharField(max_length=200, verbose_name=_('organizer name'))
    endorsement_text = models.TextField(blank=True, null=True, verbose_name=_('endorsement text'))
    endorsement_date = models.DateField(blank=True, null=True, verbose_name=_('endorsement date'))
    endorsement_ref_no = models.CharField(
        max_length=50, blank=True, null=True, verbose_name=_('reference number')
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT, verbose_name=_('Status')
    )
    recommendations = models.TextField(
        blank=True, null=True, verbose_name=_('recommendations')
    )
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='created_plans', verbose_name=_('created by')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('updated at'))
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name=_('submitted at'))
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_('approved at'))

    class Meta:
        unique_together = ('formation', 'plan_year')
        verbose_name = _('annual plan')
        verbose_name_plural = _('annual plans')
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
