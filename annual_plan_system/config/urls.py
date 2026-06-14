from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf.urls.i18n import i18n_patterns


def root_redirect(request):
    return redirect('dashboard:index')


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('', root_redirect, name='home'),
    path('admin/', admin.site.urls),
    path('auth/', include('apps.accounts.urls', namespace='accounts')),
    path('formations/', include('apps.formations.urls', namespace='formations')),
    path('plans/', include('apps.plans.urls', namespace='plans')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('ai/', include('apps.ai_assistant.urls', namespace='ai_assistant')),
    prefix_default_language=False,
)
