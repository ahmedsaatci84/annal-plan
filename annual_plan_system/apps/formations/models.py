from django.db import models
from django.utils.translation import gettext_lazy as _


class ParentFormation(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Parent Formation')
        verbose_name_plural = _('Parent Formations')
        ordering = ['name']

    def __str__(self):
        return self.name


class Formation(models.Model):
    LEVEL_COMPANY = 'COMPANY'
    LEVEL_BOARD = 'BOARD'
    LEVEL_DIVISION = 'DIVISION'
    LEVEL_SECTION = 'SECTION'
    LEVEL_UNIT = 'UNIT'

    LEVEL_CHOICES = [
        (LEVEL_COMPANY, _('Company')),
        (LEVEL_BOARD, _('Division')),
        (LEVEL_DIVISION, _('Department')),
        (LEVEL_SECTION, _('Section')),
        (LEVEL_UNIT, _('Unit')),
    ]

    name_ar = models.CharField(max_length=200, verbose_name=_('name in arabic'))
    parent_formation = models.ForeignKey(
        ParentFormation, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='formations', verbose_name=_('Parent Formation Category')
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
        return self.name_ar


