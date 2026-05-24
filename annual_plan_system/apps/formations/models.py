from django.db import models
from django.utils.translation import gettext_lazy as _


class Formation(models.Model):
    LEVEL_COMPANY = 'COMPANY'
    LEVEL_BOARD = 'BOARD'
    LEVEL_DIVISION = 'DIVISION'
    LEVEL_SECTION = 'SECTION'
    LEVEL_UNIT = 'UNIT'

    LEVEL_CHOICES = [
        (LEVEL_COMPANY, _('Company')),
        (LEVEL_BOARD, _('Board')),
        (LEVEL_DIVISION, _('Division')),
        (LEVEL_SECTION, _('Section')),
        (LEVEL_UNIT, _('Unit')),
    ]

    code = models.CharField(max_length=20, unique=True, verbose_name=_('Code'))
    name_ar = models.CharField(max_length=200, verbose_name=_('name in arabic'))
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='children', verbose_name=_('parent formation')
    )
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name=_('Level'))
    is_active = models.BooleanField(default=True, verbose_name=_('is active'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('updated at'))

    class Meta:
        verbose_name = _('formation')
        verbose_name_plural = _('formations plural')
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
