from django.db import models


class Goal(models.Model):
    plan = models.ForeignKey(
        'plans.AnnualPlan', on_delete=models.CASCADE,
        related_name='goals', verbose_name='الخطة'
    )
    sequence = models.PositiveSmallIntegerField(verbose_name='الترتيب')
    code = models.CharField(max_length=20, verbose_name='رمز الهدف')
    title = models.TextField(verbose_name='الهدف الرئيسي')
    kpi_type = models.CharField(max_length=100, verbose_name='مؤشر الأداء الرئيسي (KPI)')
    goal_type = models.CharField(max_length=50, verbose_name='نوع الهدف')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التعديل')

    class Meta:
        unique_together = ('plan', 'sequence')
        ordering = ['sequence']
        verbose_name = 'هدف'
        verbose_name_plural = 'الأهداف'
        indexes = [
            models.Index(fields=['plan']),
        ]

    def __str__(self):
        return f'({self.sequence}) {self.title[:60]}'

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f'({self.sequence})'
        super().save(*args, **kwargs)

    def completion_pct(self):
        total = self.activities.count()
        if total == 0:
            return 0
        completed = self.activities.filter(activity_status='COMPLETED').count()
        return round((completed / total) * 100)

    def status_label(self):
        from django.utils import timezone
        pct = self.completion_pct()
        if pct == 100:
            return 'مكتمل'
        if pct > 0:
            # Check for delay
            if self.activities.filter(
                activity_status__in=['DELAYED'],
            ).exists():
                return 'متأخر'
            return 'قيد الإنجاز'
        # 0% — check if any activity past end_date
        today = timezone.now().date()
        if self.activities.filter(end_date__lt=today).exists():
            return 'متأخر'
        return 'لم يبدأ'
