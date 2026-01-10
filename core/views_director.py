from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .models import User, School, Subject, AuditLog, Class, Student, Teacher
from .forms import UserCreateForm, UserUpdateForm, UserPasswordSetForm
from .auth_utils import RoleRequiredMixin, log_action


class DirectorDashboardView(RoleRequiredMixin, TemplateView):
    """Dashboard for Director of Education"""
    template_name = 'director/dashboard.html'
    allowed_roles = [User.ROLE_DEPT_EDUCATION]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get statistics
        schools = School.objects.filter(created_by=self.request.user)
        context['stats'] = {
            'total_schools': schools.count(),
            'total_classes': Class.objects.filter(school__in=schools).count(),
            'total_students': Student.objects.filter(school_class__school__in=schools).count(),
            'total_teachers': Teacher.objects.filter(school__in=schools).count(),
        }
        
        # Get schools with statistics
        schools_with_stats = schools.annotate(
            num_classes=Count('classes', distinct=True),
            num_students=Count('classes__students', distinct=True),
            num_teachers=Count('teachers', distinct=True)
        )
        
        context['schools'] = schools_with_stats
        return context


class SchoolListView(RoleRequiredMixin, ListView):
    """List of all schools for Director of Education"""
    model = School
    template_name = 'director/schools/list.html'
    context_object_name = 'schools'
    paginate_by = 20
    allowed_roles = [User.ROLE_DEPT_EDUCATION]

    def get_queryset(self):
        queryset = School.objects.filter(created_by=self.request.user)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.order_by('name')


class SchoolCreateView(RoleRequiredMixin, CreateView):
    """Create new school"""
    model = School
    template_name = 'director/schools/create.html'
    fields = ['name', 'director', 'graduating_class', 'location']
    success_url = reverse_lazy('director-school-list')
    allowed_roles = [User.ROLE_DEPT_EDUCATION]

    def form_valid(self, form):
        response = super().form_valid(form)
        school = form.save(commit=False)
        school.created_by = self.request.user
        school.save()
        
        log_action(
            user=self.request.user,
            action_type=AuditLog.ACTION_CREATE,
            model_name='School',
            object_id=self.object.id,
            details=f"Created school {self.object.name}"
        )
        messages.success(self.request, f"School '{school.name}' created successfully.")
        return response


class SchoolDetailView(RoleRequiredMixin, DetailView):
    """Detail view of a school"""
    model = School
    template_name = 'director/schools/detail.html'
    context_object_name = 'school'
    allowed_roles = [User.ROLE_DEPT_EDUCATION]

    def get_queryset(self):
        return School.objects.filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = self.object
        context['stats'] = {
            'classes': Class.objects.filter(school=school).count(),
            'students': Student.objects.filter(school_class__school=school).count(),
            'teachers': Teacher.objects.filter(school=school).count(),
        }
        return context


class SchoolUpdateView(RoleRequiredMixin, UpdateView):
    """Update school"""
    model = School
    template_name = 'director/schools/update.html'
    fields = ['name', 'director', 'graduating_class', 'location']
    success_url = reverse_lazy('director-school-list')
    allowed_roles = [User.ROLE_DEPT_EDUCATION]

    def get_queryset(self):
        return School.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(
            user=self.request.user,
            action_type=AuditLog.ACTION_UPDATE,
            model_name='School',
            object_id=self.object.id,
            details=f"Updated school {self.object.name}"
        )
        messages.success(self.request, f"School '{self.object.name}' updated successfully.")
        return response


class SchoolDeleteView(RoleRequiredMixin, DeleteView):
    """Delete school with confirmation"""
    model = School
    template_name = 'director/schools/delete.html'
    success_url = reverse_lazy('director-school-list')
    allowed_roles = [User.ROLE_DEPT_EDUCATION]

    def get_queryset(self):
        return School.objects.filter(created_by=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        log_action(
            user=self.request.user,
            action_type=AuditLog.ACTION_DELETE,
            model_name='School',
            object_id=self.object.id,
            details=f"Deleted school {self.object.name}"
        )
        messages.success(request, f"School '{self.object.name}' deleted successfully.")
        return super().delete(request, *args, **kwargs)


class DirectorUserListView(RoleRequiredMixin, ListView):
    """List of users managed by Director of Education"""
    model = User
    template_name = 'director/users/list.html'
    context_object_name = 'users'
    paginate_by = 20
    allowed_roles = [User.ROLE_DEPT_EDUCATION]

    def get_queryset(self):
        # Get users from schools created by this director
        schools = School.objects.filter(created_by=self.request.user)
        queryset = User.objects.filter(school__in=schools)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(email__icontains=search)
        
        return queryset.exclude(role=User.ROLE_SUPERUSER).exclude(
            role=User.ROLE_DEPT_EDUCATION
        ).order_by('-created_at')


class DirectorUserCreateView(RoleRequiredMixin, CreateView):
    """Create new School Administrator user"""
    model = User
    form_class = UserCreateForm
    template_name = 'director/users/create.html'
    success_url = reverse_lazy('director-user-list')
    allowed_roles = [User.ROLE_DEPT_EDUCATION]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Only allow School Administrator role
        form.fields['role'].choices = [(User.ROLE_ADMIN_SCHOOL, 'School Administrator')]
        # Only show schools created by this director
        form.fields['school'].queryset = School.objects.filter(
            created_by=self.request.user
        )
        # Hide password field - we'll set a default
        form.fields['password'].required = True
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save(commit=False)
        user.created_by = self.request.user
        
        log_action(
            user=self.request.user,
            action_type=AuditLog.ACTION_CREATE,
            model_name='User',
            object_id=self.object.id,
            details=f"Created user {self.object.username} with role School Administrator"
        )
        messages.success(self.request, f"User '{user.username}' created successfully.")
        return response


class DirectorUserDetailView(RoleRequiredMixin, DetailView):
    """Detail view of a user"""
    model = User
    template_name = 'director/users/detail.html'
    context_object_name = 'user_detail'
    allowed_roles = [User.ROLE_DEPT_EDUCATION]

    def get_queryset(self):
        schools = School.objects.filter(created_by=self.request.user)
        return User.objects.filter(school__in=schools).exclude(
            role=User.ROLE_SUPERUSER
        ).exclude(role=User.ROLE_DEPT_EDUCATION)


class DirectorUserUpdateView(RoleRequiredMixin, UpdateView):
    """Update user"""
    model = User
    form_class = UserUpdateForm
    template_name = 'director/users/update.html'
    success_url = reverse_lazy('director-user-list')
    allowed_roles = [User.ROLE_DEPT_EDUCATION]

    def get_queryset(self):
        schools = School.objects.filter(created_by=self.request.user)
        return User.objects.filter(school__in=schools).exclude(
            role=User.ROLE_SUPERUSER
        ).exclude(role=User.ROLE_DEPT_EDUCATION)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Only show schools created by this director
        form.fields['school'].queryset = School.objects.filter(
            created_by=self.request.user
        )
        # Remove role field from update form (can't change role)
        form.fields.pop('role', None)
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(
            user=self.request.user,
            action_type=AuditLog.ACTION_UPDATE,
            model_name='User',
            object_id=self.object.id,
            details=f"Updated user {self.object.username}"
        )
        messages.success(self.request, f"User '{self.object.username}' updated successfully.")
        return response


class DirectorUserDeleteView(RoleRequiredMixin, DeleteView):
    """Delete user with confirmation"""
    model = User
    template_name = 'director/users/delete.html'
    success_url = reverse_lazy('director-user-list')
    allowed_roles = [User.ROLE_DEPT_EDUCATION]

    def get_queryset(self):
        schools = School.objects.filter(created_by=self.request.user)
        return User.objects.filter(school__in=schools).exclude(
            role=User.ROLE_SUPERUSER
        ).exclude(role=User.ROLE_DEPT_EDUCATION)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        log_action(
            user=self.request.user,
            action_type=AuditLog.ACTION_DELETE,
            model_name='User',
            object_id=self.object.id,
            details=f"Deleted user {self.object.username}"
        )
        messages.success(request, f"User '{self.object.username}' deleted successfully.")
        return super().delete(request, *args, **kwargs)


class DirectorUserChangePasswordView(RoleRequiredMixin, UpdateView):
    """Change user password"""
    model = User
    template_name = 'director/users/change_password.html'
    context_object_name = 'user_detail'
    allowed_roles = [User.ROLE_DEPT_EDUCATION]

    def get_queryset(self):
        schools = School.objects.filter(created_by=self.request.user)
        return User.objects.filter(school__in=schools).exclude(
            role=User.ROLE_SUPERUSER
        ).exclude(role=User.ROLE_DEPT_EDUCATION)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = UserPasswordSetForm()
        return render(request, self.template_name, {'form': form, 'user_detail': self.object})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = UserPasswordSetForm(request.POST)
        if form.is_valid():
            self.object.set_password(form.cleaned_data['new_password'])
            self.object.save()
            log_action(
                user=request.user,
                action_type=AuditLog.ACTION_UPDATE,
                model_name='User',
                object_id=self.object.id,
                details=f"Changed password for user {self.object.username}"
            )
            messages.success(request, f"Password for '{self.object.username}' changed successfully.")
            return redirect('director-user-list')
        return render(request, self.template_name, {'form': form, 'user_detail': self.object})


class SubjectListView(RoleRequiredMixin, ListView):
    """List of all subjects (global for all schools)"""
    model = Subject
    template_name = 'director/subjects/list.html'
    context_object_name = 'subjects'
    paginate_by = 20
    allowed_roles = [User.ROLE_DEPT_EDUCATION]

    def get_queryset(self):
        queryset = Subject.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.order_by('name')


class SubjectCreateView(RoleRequiredMixin, CreateView):
    """Create new subject"""
    model = Subject
    template_name = 'director/subjects/create.html'
    fields = ['name']
    success_url = reverse_lazy('director-subject-list')
    allowed_roles = [User.ROLE_DEPT_EDUCATION]

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(
            user=self.request.user,
            action_type=AuditLog.ACTION_CREATE,
            model_name='Subject',
            object_id=self.object.id,
            details=f"Created subject {self.object.name}"
        )
        messages.success(self.request, f"Subject '{self.object.name}' created successfully.")
        return response


class SubjectDetailView(RoleRequiredMixin, DetailView):
    """Detail view of a subject"""
    model = Subject
    template_name = 'director/subjects/detail.html'
    context_object_name = 'subject'
    allowed_roles = [User.ROLE_DEPT_EDUCATION]


class SubjectUpdateView(RoleRequiredMixin, UpdateView):
    """Update subject"""
    model = Subject
    template_name = 'director/subjects/update.html'
    fields = ['name']
    success_url = reverse_lazy('director-subject-list')
    allowed_roles = [User.ROLE_DEPT_EDUCATION]

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(
            user=self.request.user,
            action_type=AuditLog.ACTION_UPDATE,
            model_name='Subject',
            object_id=self.object.id,
            details=f"Updated subject {self.object.name}"
        )
        messages.success(self.request, f"Subject '{self.object.name}' updated successfully.")
        return response


class SubjectDeleteView(RoleRequiredMixin, DeleteView):
    """Delete subject with confirmation"""
    model = Subject
    template_name = 'director/subjects/delete.html'
    success_url = reverse_lazy('director-subject-list')
    allowed_roles = [User.ROLE_DEPT_EDUCATION]

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        log_action(
            user=self.request.user,
            action_type=AuditLog.ACTION_DELETE,
            model_name='Subject',
            object_id=self.object.id,
            details=f"Deleted subject {self.object.name}"
        )
        messages.success(request, f"Subject '{self.object.name}' deleted successfully.")
        return super().delete(request, *args, **kwargs)


class DirectorReportView(RoleRequiredMixin, TemplateView):
    """Report page (placeholder for future functionality)"""
    template_name = 'director/report.html'
    allowed_roles = [User.ROLE_DEPT_EDUCATION]
