from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Activity(models.Model):
    STATUS_NOT_STARTED = 'NOT_STARTED'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_DELAYED = 'DELAYED'
    STATUS_ROLLED_OVER = 'ROLLED_OVER'
    STATUS_STOPPED = 'STOPPED'

    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, 'لم يبدأ'),
        (STATUS_IN_PROGRESS, 'قيد الإنجاز'),
        (STATUS_COMPLETED, 'مكتمل'),
        (STATUS_DELAYED, 'متأخر'),
        (STATUS_ROLLED_OVER, 'تم ترحيله'),
        (STATUS_STOPPED, 'متوقف'),
    ]

    goal = models.ForeignKey(
        'plans.Goal', on_delete=models.CASCADE,
        related_name='activities', verbose_name='الهدف'
    )
    sequence = models.PositiveSmallIntegerField(verbose_name='الترتيب')
    code = models.CharField(max_length=20, verbose_name='رمز النشاط')
    title = models.TextField(verbose_name='المهمة / النشاط')
    responsible_formation = models.ForeignKey(
        'formations.Formation', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='responsible_activities', verbose_name='التشكيل المسؤول'
    )
    required_resources = models.TextField(
        blank=True, null=True, verbose_name='الموارد المطلوبة'
    )
    start_date = models.DateField(verbose_name='تاريخ البداية')
    end_date = models.DateField(verbose_name='تاريخ النهاية')
    planned_completion_pct = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='نسبة الإنجاز المخطط (%)'
    )
    actual_completion_pct = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='نسبة الإنجاز المتحقق (%)'
    )
    activity_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED,
        verbose_name='حالة النشاط'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التعديل')

    class Meta:
        unique_together = ('goal', 'sequence')
        ordering = ['goal__sequence', 'sequence']
        verbose_name = 'نشاط'
        verbose_name_plural = 'الأنشطة'
        indexes = [
            models.Index(fields=['activity_status']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f'{self.code} — {self.title[:60]}'

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'تاريخ النهاية يجب أن يكون بعد تاريخ البداية'})

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f'{self.goal.sequence}-{self.sequence}'
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0

    def auto_update_status(self):
        from django.utils import timezone
        today = timezone.now().date()
        if self.actual_completion_pct == 100:
            self.activity_status = self.STATUS_COMPLETED
        elif self.actual_completion_pct > 0:
            if today > self.end_date:
                self.activity_status = self.STATUS_DELAYED
            else:
                self.activity_status = self.STATUS_IN_PROGRESS
        else:
            if today > self.end_date:
                self.activity_status = self.STATUS_DELAYED
            else:
                self.activity_status = self.STATUS_NOT_STARTED

    @property
    def gantt_months(self):
        """Returns list of 12 booleans: True if activity covers that month (Jan=idx0)."""
        if not self.start_date or not self.end_date:
            return [False] * 12
        result = []
        year = self.goal.plan.plan_year
        for month in range(1, 13):
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            from datetime import date
            m_start = date(year, month, 1)
            m_end = date(year, month, last_day)
            covered = self.start_date <= m_end and self.end_date >= m_start
            result.append(covered)
        return result
