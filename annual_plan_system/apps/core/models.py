from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class LookupValue(models.Model):
    CATEGORY_KPI_TYPE = 'KPI_TYPE'
    CATEGORY_GOAL_TYPE = 'GOAL_TYPE'
    CATEGORY_PROBABILITY = 'PROBABILITY'

    CATEGORY_CHOICES = [
        (CATEGORY_KPI_TYPE, 'نوع مؤشر الأداء'),
        (CATEGORY_GOAL_TYPE, 'نوع الهدف'),
        (CATEGORY_PROBABILITY, 'احتمالية المخاطر'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='الفئة')
    code = models.CharField(max_length=50, verbose_name='الرمز')
    label_ar = models.CharField(max_length=200, verbose_name='التسمية بالعربية')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتيب العرض')
    is_active = models.BooleanField(default=True, verbose_name='نشط')

    class Meta:
        unique_together = ('category', 'code')
        ordering = ['category', 'sort_order', 'label_ar']
        verbose_name = 'قيمة قائمة'
        verbose_name_plural = 'قيم القوائم'

    def __str__(self):
        return f'{self.get_category_display()} — {self.label_ar}'


class AuditLog(models.Model):
    ACTION_CREATE = 'CREATE'
    ACTION_UPDATE = 'UPDATE'
    ACTION_DELETE = 'DELETE'
    ACTION_LOGIN = 'LOGIN'
    ACTION_LOGOUT = 'LOGOUT'
    ACTION_EXPORT = 'EXPORT'

    ACTION_CHOICES = [
        (ACTION_CREATE, 'إنشاء'),
        (ACTION_UPDATE, 'تعديل'),
        (ACTION_DELETE, 'حذف'),
        (ACTION_LOGIN, 'تسجيل دخول'),
        (ACTION_LOGOUT, 'تسجيل خروج'),
        (ACTION_EXPORT, 'تصدير'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        verbose_name='المستخدم', related_name='audit_logs'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, verbose_name='الإجراء')
    model_name = models.CharField(max_length=100, verbose_name='النموذج')
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='معرف الكائن')
    object_repr = models.CharField(max_length=500, blank=True, verbose_name='تمثيل الكائن')
    changes_json = models.JSONField(null=True, blank=True, verbose_name='التغييرات')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='عنوان IP')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='وقت الإجراء')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'سجل تدقيق'
        verbose_name_plural = 'سجلات التدقيق'
        indexes = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.user} — {self.action} — {self.model_name} ({self.created_at:%Y-%m-%d %H:%M})'
