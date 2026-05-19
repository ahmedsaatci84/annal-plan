from django.db import models


class Risk(models.Model):
    PROB_LOW = 'LOW'
    PROB_MEDIUM = 'MEDIUM'
    PROB_HIGH = 'HIGH'

    PROB_CHOICES = [
        (PROB_LOW, 'منخفض'),
        (PROB_MEDIUM, 'متوسط'),
        (PROB_HIGH, 'عالي'),
    ]

    plan = models.ForeignKey(
        'plans.AnnualPlan', on_delete=models.CASCADE,
        related_name='risks', verbose_name='الخطة'
    )
    risk_description = models.TextField(verbose_name='الخطر المحتمل')
    probability = models.CharField(
        max_length=10, choices=PROB_CHOICES, verbose_name='احتمالية الحدوث'
    )
    impact_description = models.TextField(verbose_name='التأثير')
    treatment_plan = models.TextField(verbose_name='خطة المعالجة البديلة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        verbose_name = 'مخاطرة'
        verbose_name_plural = 'المخاطر'
        ordering = ['probability', 'id']
        indexes = [
            models.Index(fields=['plan']),
            models.Index(fields=['probability']),
        ]

    def __str__(self):
        return f'{self.get_probability_display()} — {self.risk_description[:60]}'
