from django import forms
from django.utils import timezone
from .models import AnnualPlan, SwotAnalysis, Goal, Activity, Risk


class PlanHeaderForm(forms.ModelForm):
    class Meta:
        model = AnnualPlan
        fields = (
            'formation', 'plan_year', 'manager_name', 'organizer_name',
            'endorsement_text', 'endorsement_date', 'endorsement_ref_no',
        )
        labels = {
            'formation': 'التشكيل',
            'plan_year': 'سنة الخطة',
            'manager_name': 'اسم مدير التشكيل',
            'organizer_name': 'اسم منظم الاستمارة',
            'endorsement_text': 'نص المصادقة',
            'endorsement_date': 'تاريخ المصادقة',
            'endorsement_ref_no': 'رقم الإشارة',
        }
        widgets = {
            'formation': forms.Select(attrs={'class': 'form-select'}),
            'plan_year': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 2020, 'max': 2030,
                'value': timezone.now().year
            }),
            'manager_name': forms.TextInput(attrs={'class': 'form-control'}),
            'organizer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'endorsement_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'endorsement_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'endorsement_ref_no': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        }


class SwotForm(forms.ModelForm):
    class Meta:
        model = SwotAnalysis
        fields = ('strengths', 'weaknesses', 'opportunities', 'threats')
        labels = {
            'strengths': 'نقاط القوة',
            'weaknesses': 'نقاط الضعف',
            'opportunities': 'الفرص',
            'threats': 'التهديدات',
        }
        widgets = {
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'weaknesses': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'opportunities': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'threats': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ('title', 'kpi_type', 'goal_type')
        labels = {
            'title': 'الهدف الرئيسي',
            'kpi_type': 'مؤشر الأداء الرئيسي (KPI)',
            'goal_type': 'نوع الهدف',
        }
        widgets = {
            'title': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'kpi_type': forms.Select(attrs={'class': 'form-select'}),
            'goal_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.core.models import LookupValue
        kpi_qs = LookupValue.objects.filter(category='KPI_TYPE', is_active=True).order_by('sort_order')
        goal_qs = LookupValue.objects.filter(category='GOAL_TYPE', is_active=True).order_by('sort_order')
        self.fields['kpi_type'].widget = forms.Select(
            choices=[('', '— اختر —')] + [(lv.code, lv.label_ar) for lv in kpi_qs],
            attrs={'class': 'form-select'}
        )
        self.fields['goal_type'].widget = forms.Select(
            choices=[('', '— اختر —')] + [(lv.code, lv.label_ar) for lv in goal_qs],
            attrs={'class': 'form-select'}
        )


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = (
            'title', 'responsible_formation', 'required_resources',
            'start_date', 'end_date', 'planned_completion_pct', 'activity_status',
        )
        labels = {
            'title': 'المهمة / النشاط',
            'responsible_formation': 'التشكيل المسؤول',
            'required_resources': 'الموارد المطلوبة',
            'start_date': 'تاريخ البداية',
            'end_date': 'تاريخ النهاية',
            'planned_completion_pct': 'نسبة الإنجاز المخطط (%)',
            'activity_status': 'حالة النشاط',
        }
        widgets = {
            'title': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'responsible_formation': forms.Select(attrs={'class': 'form-select'}),
            'required_resources': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'planned_completion_pct': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'activity_status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')
        return cleaned


class ActivityProgressForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ('actual_completion_pct', 'activity_status')
        labels = {
            'actual_completion_pct': 'نسبة الإنجاز المتحقق (%)',
            'activity_status': 'حالة النشاط',
        }
        widgets = {
            'actual_completion_pct': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'activity_status': forms.Select(attrs={'class': 'form-select'}),
        }


class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = ('risk_description', 'probability', 'impact_description', 'treatment_plan')
        labels = {
            'risk_description': 'الخطر المحتمل',
            'probability': 'احتمالية الحدوث',
            'impact_description': 'التأثير',
            'treatment_plan': 'خطة المعالجة البديلة',
        }
        widgets = {
            'risk_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'probability': forms.Select(attrs={'class': 'form-select'}),
            'impact_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'treatment_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class RecommendationsForm(forms.ModelForm):
    class Meta:
        model = AnnualPlan
        fields = ('recommendations',)
        labels = {'recommendations': 'التوصيات النهائية'}
        widgets = {
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
        }


class WorkflowCommentForm(forms.Form):
    comment = forms.CharField(
        label='التعليق',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )


class PlanStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(
        label='الحالة',
        choices=AnnualPlan.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    comment = forms.CharField(
        label='التعليق',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def __init__(self, *args, current_status=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_status = current_status

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        comment = cleaned_data.get('comment', '').strip()
        if status == AnnualPlan.STATUS_REJECTED and not comment:
            self.add_error('comment', 'سبب الرفض مطلوب عند تحويل الحالة إلى مرفوضة.')
        if (
            self.current_status == AnnualPlan.STATUS_APPROVED
            and status
            and status != AnnualPlan.STATUS_APPROVED
            and not comment
        ):
            self.add_error('comment', 'التعليق مطلوب عند تحويل الخطة من معتمدة إلى حالة أخرى.')
        return cleaned_data
