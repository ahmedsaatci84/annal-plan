from django.db import models


class SwotAnalysis(models.Model):
    plan = models.OneToOneField(
        'plans.AnnualPlan', on_delete=models.CASCADE,
        related_name='swot', verbose_name='الخطة'
    )
    strengths = models.TextField(blank=True, null=True, verbose_name='نقاط القوة')
    weaknesses = models.TextField(blank=True, null=True, verbose_name='نقاط الضعف')
    opportunities = models.TextField(blank=True, null=True, verbose_name='الفرص')
    threats = models.TextField(blank=True, null=True, verbose_name='التهديدات')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التعديل')

    class Meta:
        verbose_name = 'تحليل SWOT'
        verbose_name_plural = 'تحليلات SWOT'

    def __str__(self):
        return f'SWOT — {self.plan}'
