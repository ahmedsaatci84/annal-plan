from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy

from apps.core.mixins import AdminRequiredMixin, RoleRequiredMixin
from apps.core.middleware import log_action, AuditLogMiddleware
from .forms import LoginForm, UserCreateForm, UserProfileForm, CustomPasswordChangeForm
from .models import UserProfile


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            ip = AuditLogMiddleware.get_client_ip(request)
            log_action(user, 'LOGIN', 'User', user, ip_address=ip)
            return redirect(request.GET.get('next', 'dashboard:index'))
    else:
        form = LoginForm(request)
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    if request.method == 'POST':
        ip = AuditLogMiddleware.get_client_ip(request)
        log_action(request.user, 'LOGOUT', 'User', request.user, ip_address=ip)
        logout(request)
    return redirect('accounts:login')


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'تم تغيير كلمة المرور بنجاح.')
            return redirect('dashboard:index')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'accounts/password_change.html', {'form': form})


class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.select_related('profile', 'profile__formation').order_by('username')


class UserCreateView(AdminRequiredMixin, CreateView):
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'user_form': UserCreateForm(),
            'profile_form': UserProfileForm(),
        })

    def post(self, request, *args, **kwargs):
        user_form = UserCreateForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            ip = AuditLogMiddleware.get_client_ip(request)
            log_action(request.user, 'CREATE', 'UserProfile', profile, ip_address=ip)
            messages.success(request, 'تم إنشاء المستخدم بنجاح.')
            return redirect(self.success_url)
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
        })


class UserEditView(AdminRequiredMixin, UpdateView):
    model = User
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def get(self, request, *args, **kwargs):
        user_obj = get_object_or_404(User, pk=kwargs['pk'])
        profile, _ = UserProfile.objects.get_or_create(user=user_obj)
        return render(request, self.template_name, {
            'user_form': UserCreateForm(instance=user_obj),
            'profile_form': UserProfileForm(instance=profile),
            'edit_mode': True,
            'target_user': user_obj,
        })

    def post(self, request, *args, **kwargs):
        user_obj = get_object_or_404(User, pk=kwargs['pk'])
        profile, _ = UserProfile.objects.get_or_create(user=user_obj)
        # For edit we don't require password re-entry
        profile_form = UserProfileForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            ip = AuditLogMiddleware.get_client_ip(request)
            log_action(request.user, 'UPDATE', 'UserProfile', profile, ip_address=ip)
            messages.success(request, 'تم تحديث بيانات المستخدم.')
            return redirect(self.success_url)
        return render(request, self.template_name, {
            'user_form': UserCreateForm(instance=user_obj),
            'profile_form': profile_form,
            'edit_mode': True,
            'target_user': user_obj,
        })


@login_required
def toggle_user_active(request, pk):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_admin():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    if request.method == 'POST':
        target_user = get_object_or_404(User, pk=pk)
        target_user.is_active = not target_user.is_active
        target_user.save(update_fields=['is_active'])
        status = 'مفعّل' if target_user.is_active else 'معطّل'
        messages.success(request, f'تم {status} المستخدم بنجاح.')
    return redirect('accounts:user_list')
