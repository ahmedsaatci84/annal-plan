from django.db import models


class Formation(models.Model):
    LEVEL_COMPANY = 'COMPANY'
    LEVEL_BOARD = 'BOARD'
    LEVEL_DIVISION = 'DIVISION'
    LEVEL_SECTION = 'SECTION'
    LEVEL_UNIT = 'UNIT'

    LEVEL_CHOICES = [
        (LEVEL_COMPANY, 'شركة'),
        (LEVEL_BOARD, 'هيأة'),
        (LEVEL_DIVISION, 'قسم'),
        (LEVEL_SECTION, 'شعبة'),
        (LEVEL_UNIT, 'وحدة'),
    ]

    code = models.CharField(max_length=20, unique=True, verbose_name='الرمز')
    name_ar = models.CharField(max_length=200, verbose_name='الاسم بالعربية')
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='children', verbose_name='التشكيل الأعلى'
    )
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name='المستوى')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التعديل')

    class Meta:
        verbose_name = 'تشكيل'
        verbose_name_plural = 'التشكيلات'
        ordering = ['level', 'name_ar']
        indexes = [
            models.Index(fields=['level']),
        ]

    def __str__(self):
        return f'{self.name_ar} ({self.code})'

    def get_ancestors(self):
        ancestors = []
        current = self.parent
        while current:
            ancestors.insert(0, current)
            current = current.parent
        return ancestors

    def get_descendants(self):
        result = []
        for child in self.children.filter(is_active=True):
            result.append(child)
            result.extend(child.get_descendants())
        return result
