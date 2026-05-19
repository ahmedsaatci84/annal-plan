from django import forms
from .models import Formation


class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        fields = ('code', 'name_ar', 'parent', 'level', 'is_active')
        labels = {
            'code': 'الرمز',
            'name_ar': 'الاسم بالعربية',
            'parent': 'التشكيل الأعلى',
            'level': 'المستوى',
            'is_active': 'نشط',
        }
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'name_ar': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
        }
