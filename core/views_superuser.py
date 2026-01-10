import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, Avg
from django.utils import timezone

from .models import User, School, Class, Student, Teacher, Subject, AuditLog, Grade
from .forms import UserCreateForm, UserUpdateForm, UserPasswordSetForm, LogFilterForm
from .auth_utils import RoleRequiredMixin, log_action

class SuperuserDashboardView(RoleRequiredMixin, TemplateView):
    template_name = 'superuser/dashboard.html'
    allowed_roles = [User.ROLE_SUPERUSER]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = User.objects.exclude(role=User.ROLE_SUPERUSER).count()
        context['total_schools'] = School.objects.count()
        context['recent_logs'] = AuditLog.objects.all()[:10]
        return context

class UserListView(RoleRequiredMixin, ListView):
    model = User
    template_name = 'superuser/users/list.html'
    context_object_name = 'users'
    paginate_by = 20
    allowed_roles = [User.ROLE_SUPERUSER]

    def get_queryset(self):
        return User.objects.exclude(role=User.ROLE_SUPERUSER).order_by('-created_at')

class UserCreateView(RoleRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'superuser/users/create.html'
    success_url = reverse_lazy('user-list')
    allowed_roles = [User.ROLE_SUPERUSER]

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(
            user=self.request.user,
            action_type=AuditLog.ACTION_CREATE,
            model_name='User',
            object_id=self.object.id,
            details=f"Created user {self.object.username} with role {self.object.role}"
        )
        messages.success(self.request, f"User {self.object.username} created successfully.")
        return response

class UserDetailView(RoleRequiredMixin, DetailView):
    model = User
    template_name = 'superuser/users/detail.html'
    context_object_name = 'user_detail'
    allowed_roles = [User.ROLE_SUPERUSER]

class UserUpdateView(RoleRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'superuser/users/update.html'
    success_url = reverse_lazy('user-list')
    allowed_roles = [User.ROLE_SUPERUSER]

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(
            user=self.request.user,
            action_type=AuditLog.ACTION_UPDATE,
            model_name='User',
            object_id=self.object.id,
            details=f"Updated user {self.object.username}"
        )
        messages.success(self.request, f"User {self.object.username} updated successfully.")
        return response

class UserDeleteView(RoleRequiredMixin, DeleteView):
    model = User
    template_name = 'superuser/users/delete.html'
    success_url = reverse_lazy('user-list')
    allowed_roles = [User.ROLE_SUPERUSER]

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        log_action(
            user=self.request.user,
            action_type=AuditLog.ACTION_DELETE,
            model_name='User',
            object_id=self.object.id,
            details=f"Deleted user {self.object.username}"
        )
        messages.success(self.request, f"User {self.object.username} deleted successfully.")
        return super().delete(request, *args, **kwargs)

class UserChangePasswordView(RoleRequiredMixin, View):
    allowed_roles = [User.ROLE_SUPERUSER]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = UserPasswordSetForm()
        return render(request, 'superuser/users/change_password.html', {'form': form, 'user_detail': user})

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = UserPasswordSetForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            log_action(
                user=request.user,
                action_type=AuditLog.ACTION_UPDATE,
                model_name='User',
                object_id=user.id,
                details=f"Changed password for user {user.username}"
            )
            messages.success(request, f"Password for {user.username} changed successfully.")
            return redirect('user-list')
        return render(request, 'superuser/users/change_password.html', {'form': form, 'user_detail': user})

class SchoolStatisticsView(RoleRequiredMixin, TemplateView):
    template_name = 'superuser/statistics/index.html'
    allowed_roles = [User.ROLE_SUPERUSER]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = {
            'total_schools': School.objects.count(),
            'total_classes': Class.objects.count(),
            'total_students': Student.objects.count(),
            'total_teachers': Teacher.objects.count(),
            'total_subjects': Subject.objects.count(),
        }
        
        schools = School.objects.annotate(
            num_classes=Count('classes', distinct=True),
            num_students=Count('classes__students', distinct=True),
            num_teachers=Count('teachers', distinct=True)
        )
        
        # Calculate average grade per school if possible
        # This is complex because Grades are linked to students and subjects.
        # School -> Class -> Student -> Grade
        for school in schools:
            avg_grade = Grade.objects.filter(student__school_class__school=school).aggregate(Avg('grade'))['grade__avg']
            school.avg_grade = round(avg_grade, 2) if avg_grade else "N/A"

        context['schools_stats'] = schools
        return context

class AuditLogListView(RoleRequiredMixin, ListView):
    model = AuditLog
    template_name = 'superuser/logs/index.html'
    context_object_name = 'logs'
    paginate_by = 50
    allowed_roles = [User.ROLE_SUPERUSER]

    def get_queryset(self):
        queryset = AuditLog.objects.all().select_related('user')
        form = LogFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('user'):
                queryset = queryset.filter(user=form.cleaned_data['user'])
            if form.cleaned_data.get('action_type'):
                queryset = queryset.filter(action_type=form.cleaned_data['action_type'])
            if form.cleaned_data.get('model_name'):
                queryset = queryset.filter(model_name__icontains=form.cleaned_data['model_name'])
            if form.cleaned_data.get('date_from'):
                queryset = queryset.filter(created_at__date__gte=form.cleaned_data['date_from'])
            if form.cleaned_data.get('date_to'):
                queryset = queryset.filter(created_at__date__lte=form.cleaned_data['date_to'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = LogFilterForm(self.request.GET)
        return context

def export_logs_to_csv(request):
    if not request.user.is_authenticated or request.user.role != User.ROLE_SUPERUSER:
        return HttpResponseForbidden()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="audit_logs_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'User', 'Action', 'Model', 'ID', 'Details'])

    queryset = AuditLog.objects.all().select_related('user')
    
    # Apply filters from GET params if any
    form = LogFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('user'):
            queryset = queryset.filter(user=form.cleaned_data['user'])
        if form.cleaned_data.get('action_type'):
            queryset = queryset.filter(action_type=form.cleaned_data['action_type'])
        if form.cleaned_data.get('model_name'):
            queryset = queryset.filter(model_name__icontains=form.cleaned_data['model_name'])
        if form.cleaned_data.get('date_from'):
            queryset = queryset.filter(created_at__date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            queryset = queryset.filter(created_at__date__lte=form.cleaned_data['date_to'])

    for log in queryset:
        writer.writerow([
            log.created_at,
            log.user.username if log.user else 'System',
            log.action_type,
            log.model_name,
            log.object_id,
            log.details
        ])

    return response
