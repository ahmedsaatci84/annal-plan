from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Formation, ParentFormation


class ParentFormationForm(forms.ModelForm):
    class Meta:
        model = ParentFormation
        fields = ('name', 'description', 'is_active')
        labels = {
            'name': _('Name'),
            'description': _('Description'),
            'is_active': _('Is Active'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        fields = ('name_ar', 'parent_formation', 'level', 'is_active')
        labels = {
            'name_ar': _('name in arabic'),
            'parent_formation': _('Parent Formation Category'),
            'level': _('Level'),
            'is_active': _('is active'),
        }
        widgets = {
            'name_ar': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_formation': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
        }
