from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from apps.core.mixins import AdminRequiredMixin, RoleRequiredMixin
from apps.core.middleware import log_action, AuditLogMiddleware
from .models import Formation, ParentFormation
from .forms import FormationForm, ParentFormationForm


# ── Parent Formation Views ────────────────────────────────────────────────────

class ParentFormationListView(AdminRequiredMixin, ListView):
    model = ParentFormation
    template_name = 'formations/parent_formation_list.html'
    context_object_name = 'parent_formations'

    def get_queryset(self):
        return ParentFormation.objects.prefetch_related('formations').order_by('name')


def parent_formation_create(request):
    if not request.user.is_authenticated or not request.user.profile.is_admin():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    if request.method == 'POST':
        form = ParentFormationForm(request.POST)
        if form.is_valid():
            obj = form.save()
            ip = AuditLogMiddleware.get_client_ip(request)
            log_action(request.user, 'CREATE', 'ParentFormation', obj, ip_address=ip)
            messages.success(request, _('Parent Formation created successfully.'))
            return redirect('formations:parent_list')
    else:
        form = ParentFormationForm()
    return render(request, 'formations/parent_formation_form.html', {
        'form': form, 'title': _('Create Parent Formation')
    })


def parent_formation_edit(request, pk):
    if not request.user.is_authenticated or not request.user.profile.is_admin():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    obj = get_object_or_404(ParentFormation, pk=pk)
    if request.method == 'POST':
        form = ParentFormationForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            ip = AuditLogMiddleware.get_client_ip(request)
            log_action(request.user, 'UPDATE', 'ParentFormation', obj, ip_address=ip)
            messages.success(request, _('Parent Formation updated successfully.'))
            return redirect('formations:parent_list')
    else:
        form = ParentFormationForm(instance=obj)
    return render(request, 'formations/parent_formation_form.html', {
        'form': form, 'title': _('Edit Parent Formation'), 'object': obj
    })


def parent_formation_delete(request, pk):
    if not request.user.is_authenticated or not request.user.profile.is_admin():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    obj = get_object_or_404(ParentFormation, pk=pk)
    if request.method == 'POST':
        ip = AuditLogMiddleware.get_client_ip(request)
        log_action(request.user, 'DELETE', 'ParentFormation', obj, ip_address=ip)
        obj.delete()
        messages.success(request, _('Parent Formation deleted successfully.'))
        return redirect('formations:parent_list')
    return render(request, 'formations/parent_formation_confirm_delete.html', {'object': obj})


# ── Formation Views ───────────────────────────────────────────────────────────


class FormationListView(AdminRequiredMixin, ListView):
    model = Formation
    template_name = 'formations/formation_list.html'
    context_object_name = 'formations'

    def get_queryset(self):
        return Formation.objects.select_related('parent_formation').order_by('level', 'name_ar')


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
            messages.success(request, _('Formation created successfully.'))
            return redirect('formations:list')
    else:
        form = FormationForm()
    return render(request, 'formations/formation_form.html', {'form': form, 'title': _('Create Formation')})


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
            messages.success(request, _('Formation updated successfully.'))
            return redirect('formations:list')
    else:
        form = FormationForm(instance=formation)
    return render(request, 'formations/formation_form.html', {
        'form': form, 'title': _('Edit Formation'), 'formation': formation
    })


def formation_delete(request, pk):
    if not request.user.is_authenticated or not request.user.profile.is_admin():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    formation = get_object_or_404(Formation, pk=pk)
    if request.method == 'POST':
        ip = AuditLogMiddleware.get_client_ip(request)
        log_action(request.user, 'DELETE', 'Formation', formation, ip_address=ip)
        formation.delete()
        messages.success(request, _('Formation deleted successfully.'))
        return redirect('formations:list')
    return render(request, 'formations/formation_confirm_delete.html', {'formation': formation})


def formation_tree_api(request):
    """JSON API: returns active formations list."""
    if not request.user.is_authenticated:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()

    formations = Formation.objects.filter(is_active=True).select_related('parent_formation').order_by('level', 'name_ar')
    data = [
        {
            'id': f.id,
            'name_ar': f.name_ar,
            'level': f.level,
            'parent_formation': f.parent_formation.name if f.parent_formation else None,
        }
        for f in formations
    ]
    return JsonResponse({'formations': data})
