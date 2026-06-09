from datetime import date
from django.conf import settings


def app_info(request):
    return {
        'APP_VERSION': getattr(settings, 'APP_VERSION', '1.0.0'),
        'CURRENT_YEAR': date.today().year,
    }
