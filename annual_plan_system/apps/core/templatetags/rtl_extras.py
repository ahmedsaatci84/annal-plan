from django import template

register = template.Library()


@register.filter(name='pct_color')
def pct_color(value):
    """Return a Bootstrap color class based on completion percentage."""
    try:
        v = int(value)
    except (TypeError, ValueError):
        return 'secondary'
    if v == 100:
        return 'success'
    if v >= 60:
        return 'warning'
    if v > 0:
        return 'info'
    return 'secondary'


@register.filter(name='status_badge')
def status_badge(status):
    mapping = {
        'DRAFT': 'secondary',
        'SUBMITTED': 'primary',
        'UNDER_REVIEW': 'info',
        'APPROVED': 'success',
        'REJECTED': 'danger',
        'ARCHIVED': 'dark',
    }
    return mapping.get(status, 'secondary')


@register.filter(name='status_label')
def status_label(status):
    mapping = {
        'DRAFT': 'مسودة',
        'SUBMITTED': 'مقدمة',
        'UNDER_REVIEW': 'قيد المراجعة',
        'APPROVED': 'معتمدة',
        'REJECTED': 'مرفوضة',
        'ARCHIVED': 'مؤرشفة',
    }
    return mapping.get(status, status)


@register.filter(name='activity_status_label')
def activity_status_label(status):
    mapping = {
        'NOT_STARTED': 'لم يبدأ',
        'IN_PROGRESS': 'قيد الإنجاز',
        'COMPLETED': 'مكتمل',
        'DELAYED': 'متأخر',
        'ROLLED_OVER': 'تم ترحيله',
        'STOPPED': 'متوقف',
    }
    return mapping.get(status, status)


@register.filter(name='activity_status_color')
def activity_status_color(status):
    mapping = {
        'NOT_STARTED': '#e9ecef',
        'IN_PROGRESS': '#ffc107',
        'COMPLETED': '#28a745',
        'DELAYED': '#dc3545',
        'ROLLED_OVER': '#fd7e14',
        'STOPPED': '#6c757d',
    }
    return mapping.get(status, '#e9ecef')


@register.filter(name='probability_label')
def probability_label(prob):
    mapping = {
        'LOW': 'منخفض',
        'MEDIUM': 'متوسط',
        'HIGH': 'عالي',
    }
    return mapping.get(prob, prob)


@register.filter(name='role_label')
def role_label(role):
    mapping = {
        'ADMIN': 'مسؤول النظام',
        'MANAGER': 'مدير',
        'ORGANIZER': 'منظم',
        'REVIEWER': 'مراجع',
        'VIEWER': 'مشاهد',
    }
    return mapping.get(role, role)


@register.simple_tag
def arabic_month(month_num):
    months = {
        1: 'كانون الثاني',
        2: 'شباط',
        3: 'آذار',
        4: 'نيسان',
        5: 'أيار',
        6: 'حزيران',
        7: 'تموز',
        8: 'آب',
        9: 'أيلول',
        10: 'تشرين الأول',
        11: 'تشرين الثاني',
        12: 'كانون الأول',
    }
    return months.get(month_num, str(month_num))
