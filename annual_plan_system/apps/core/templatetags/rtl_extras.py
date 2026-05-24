from django import template
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils import translation
import calendar

register = template.Library()


@register.filter(name='strip_lang_prefix')
def strip_lang_prefix(full_path):
    """Strip any non-default language prefix from a URL path.

    Used in the language switcher form so that translate_url() always
    receives a clean (unprefixed) path and can resolve it correctly.
    """
    for lang_code, _ in settings.LANGUAGES:
        if lang_code == settings.LANGUAGE_CODE:
            continue  # default language has no prefix
        prefix = f'/{lang_code}/'
        if full_path.startswith(prefix):
            return '/' + full_path[len(prefix):]
        if full_path == f'/{lang_code}':
            return '/'
    return full_path


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
        'DRAFT': 'draft',
        'SUBMITTED': 'submitted',
        'UNDER_REVIEW': 'review',
        'APPROVED': 'approved',
        'REJECTED': 'rejected',
        'ARCHIVED': 'archived',
    }
    return mapping.get(status, 'draft')


@register.filter(name='activity_status_class')
def activity_status_class(status):
    mapping = {
        'NOT_STARTED': 'not-started',
        'IN_PROGRESS': 'in-progress',
        'COMPLETED': 'completed',
        'DELAYED': 'delayed',
        'ROLLED_OVER': 'rolled-over',
        'STOPPED': 'stopped',
    }
    return mapping.get(status, 'not-started')


@register.filter(name='status_label')
def status_label(status):
    mapping = {
        'DRAFT': _('Draft'),
        'SUBMITTED': _('Submitted'),
        'UNDER_REVIEW': _('Under Review'),
        'APPROVED': _('Approved'),
        'REJECTED': _('Rejected'),
        'ARCHIVED': _('Archived'),
    }
    return mapping.get(status, status)


@register.filter(name='activity_status_label')
def activity_status_label(status):
    mapping = {
        'NOT_STARTED': _('Not Started'),
        'IN_PROGRESS': _('In Progress'),
        'COMPLETED': _('Completed'),
        'DELAYED': _('Delayed'),
        'ROLLED_OVER': _('Rolled Over'),
        'STOPPED': _('Stopped'),
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
        'LOW': _('Low'),
        'MEDIUM': _('Medium'),
        'HIGH': _('High'),
    }
    return mapping.get(prob, prob)


@register.filter(name='role_label')
def role_label(role):
    mapping = {
        'ADMIN': _('System Admin'),
        'MANAGER': _('Formation Manager'),
        'ORGANIZER': _('Form Organizer'),
        'REVIEWER': _('Reviewer'),
        'VIEWER': _('Viewer'),
    }
    return mapping.get(role, role)


@register.simple_tag
def arabic_month(month_num):
    """Return month name in the active language.

    For Arabic: uses traditional Levantine/Iraqi month names.
    For English: uses standard Gregorian month names.
    """
    lang = translation.get_language() or 'en'
    if lang.startswith('ar'):
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
    try:
        return calendar.month_name[int(month_num)]
    except (ValueError, IndexError, TypeError):
        return str(month_num)


@register.simple_tag(takes_context=True)
def is_rtl(context):
    """Return True when the active language is RTL (Arabic)."""
    request = context.get('request')
    if request:
        lang = getattr(request, 'LANGUAGE_CODE', translation.get_language() or 'en')
    else:
        lang = translation.get_language() or 'en'
    return lang.startswith('ar')



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
