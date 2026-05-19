from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView
from django.http import JsonResponse

from apps.core.mixins import AdminRequiredMixin, RoleRequiredMixin
from apps.core.middleware import log_action, AuditLogMiddleware
from .models import Formation
from .forms import FormationForm


class FormationListView(AdminRequiredMixin, ListView):
    model = Formation
    template_name = 'formations/formation_list.html'
    context_object_name = 'formations'

    def get_queryset(self):
        return Formation.objects.select_related('parent').order_by('level', 'name_ar')


def formation_create(request):
    if not request.user.is_authenticated or not request.user.profile.is_admin():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    if request.method == 'POST':
        form = FormationForm(request.POST)
        if form.is_valid():
            formation = form.save()
            ip = AuditLogMiddleware.get_client_ip(request)
            log_action(request.user, 'CREATE', 'Formation', formation, ip_address=ip)
            messages.success(request, 'تم إنشاء التشكيل بنجاح.')
            return redirect('formations:list')
    else:
        form = FormationForm()
    return render(request, 'formations/formation_form.html', {'form': form, 'title': 'إنشاء تشكيل'})


def formation_edit(request, pk):
    if not request.user.is_authenticated or not request.user.profile.is_admin():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    formation = get_object_or_404(Formation, pk=pk)
    if request.method == 'POST':
        form = FormationForm(request.POST, instance=formation)
        if form.is_valid():
            form.save()
            ip = AuditLogMiddleware.get_client_ip(request)
            log_action(request.user, 'UPDATE', 'Formation', formation, ip_address=ip)
            messages.success(request, 'تم تحديث التشكيل بنجاح.')
            return redirect('formations:list')
    else:
        form = FormationForm(instance=formation)
    return render(request, 'formations/formation_form.html', {
        'form': form, 'title': 'تعديل تشكيل', 'formation': formation
    })


def formation_tree_api(request):
    """JSON API: returns formation hierarchy."""
    if not request.user.is_authenticated:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()

    def build_node(f):
        return {
            'id': f.id,
            'code': f.code,
            'name_ar': f.name_ar,
            'level': f.level,
            'children': [build_node(c) for c in f.children.filter(is_active=True)],
        }

    roots = Formation.objects.filter(parent__isnull=True, is_active=True)
    return JsonResponse({'tree': [build_node(r) for r in roots]})
