from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


def root_redirect(request):
    return redirect('dashboard:index')


urlpatterns = [
    path('', root_redirect, name='home'),
    path('admin/', admin.site.urls),
    path('auth/', include('apps.accounts.urls', namespace='accounts')),
    path('formations/', include('apps.formations.urls', namespace='formations')),
    path('plans/', include('apps.plans.urls', namespace='plans')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
]
