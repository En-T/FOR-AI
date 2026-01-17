import csv
import json
import logging
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.db.models import Avg, Count, Q, Prefetch
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView,
    FormView
)
from .mixins import (
    SuperuserRequiredMixin, EducationDeptRequiredMixin, SchoolAdminRequiredMixin,
    SchoolOwnerRequiredMixin, ClassOwnerRequiredMixin, StudentOwnerRequiredMixin, 
    TeacherOwnerRequiredMixin
)
from .models import (
    User, School, ClassGroup, Student, Teacher, Subject, 
    ClassSubjectGroup, StudentSubjectGroup, Grade, AuditLog
)
from .forms import (
    SchoolForm, UserForm, UserChangePasswordForm, SubjectForm, ClassForm,
    StudentForm, TeacherForm, AssignTeacherToSubjectForm, 
    DistributeStudentsToSubgroupsForm, AssignTeacherToGroupForm, GradeJournalForm
)
from .utils import (
    log_action, get_student_average_by_quarter, get_class_average, 
    get_school_average, calculate_statistics, get_user_school, 
    get_system_statistics, get_class_subject_groups, get_teacher_assignments,
    parse_log_file
)

logger = logging.getLogger('schools')

# ==================== SUPERUSER VIEWS ====================

class SuperuserDashboardView(SuperuserRequiredMixin, TemplateView):
    template_name = 'schools/superuser/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statistics'] = get_system_statistics()
        
        recent_logs = AuditLog.objects.select_related('actor').order_by('-created_at')[:10]
        context['recent_logs'] = recent_logs
        
        return context

class SuperuserAddUserView(SuperuserRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = 'schools/superuser/user_form.html'
    success_url = reverse_lazy('schools:superuser-user-list')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        password = form.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        else:
            # Генерация пароля
            import secrets
            password = secrets.token_urlsafe(8)
            user.set_password(password)
        
        user.save()
        
        log_action(self.request.user, 'create', 'User', user.id, f"Created user: {user.email}")
        messages.success(self.request, _('Пользователь успешно создан'))
        
        return super().form_valid(form)

class SuperuserUserListView(SuperuserRequiredMixin, ListView):
    model = User
    template_name = 'schools/superuser/user_list.html'
    context_object_name = 'users'
    
    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id).select_related()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role_filter = self.request.GET.get('role', '')
        if role_filter:
            context['users'] = context['users'].filter(role=role_filter)
        context['role_filter'] = role_filter
        return context

class SuperuserViewLogsView(SuperuserRequiredMixin, TemplateView):
    template_name = 'schools/superuser/logs.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get('search', '')
        
        # Парсим лог-файл
        context['logs'] = parse_log_file(limit=100, search_term=search)
        context['search'] = search
        
        # Также показываем логи из базы данных
        db_logs = AuditLog.objects.select_related('actor').order_by('-created_at')
        if search:
            db_logs = db_logs.filter(Q(action__icontains=search) | Q(model_name__icontains=search))
        context['db_logs'] = db_logs[:100]
        
        return context

# ==================== EDUCATION DEPARTMENT VIEWS ====================

class EducationDeptDashboardView(EducationDeptRequiredMixin, TemplateView):
    template_name = 'schools/education_dept/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schools = School.objects.filter(education_dept=self.request.user).select_related()
        
        school_stats = []
        for school in schools:
            stats = calculate_statistics(school)
            school_stats.append({
                'school': school,
                'stats': stats
            })
        
        context['school_stats'] = school_stats
        return context

class SchoolListView(EducationDeptRequiredMixin, ListView):
    model = School
    template_name = 'schools/education_dept/school_list.html'
    context_object_name = 'schools'
    
    def get_queryset(self):
        return School.objects.filter(education_dept=self.request.user).select_related()

class SchoolCreateView(EducationDeptRequiredMixin, CreateView):
    model = School
    form_class = SchoolForm
    template_name = 'schools/education_dept/school_form.html'
    
    def form_valid(self, form):
        school = form.save(commit=False)
        school.education_dept = self.request.user
        school.save()
        
        log_action(self.request.user, 'create', 'School', school.id, f"Created school: {school.name}")
        messages.success(self.request, _('Школа успешно создана'))
        
        return redirect('schools:education_dept-school-list')

class SchoolDetailView(EducationDeptRequiredMixin, DetailView):
    model = School
    template_name = 'schools/education_dept/school_detail.html'
    context_object_name = 'school'
    pk_url_kwarg = 'school_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = self.object
        
        stats = calculate_statistics(school)
        context['statistics'] = stats
        
        classes = school.classes.annotate(
            student_count=Count('students'),
            average_grade=Avg('students__grades__grade', filter=Q(students__grades__quarter__in=['q1', 'q2', 'q3', 'q4']))
        )
        context['classes'] = classes
        
        return context

class SchoolUpdateView(EducationDeptRequiredMixin, UpdateView):
    model = School
    form_class = SchoolForm
    template_name = 'schools/education_dept/school_form.html'
    pk_url_kwarg = 'school_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context
    
    def form_valid(self, form):
        school = form.save()
        log_action(self.request.user, 'update', 'School', school.id, f"Updated school: {school.name}")
        messages.success(self.request, _('Школа успешно обновлена'))
        return redirect('schools:education_dept-school-detail', school_id=school.id)

class SchoolDeleteView(EducationDeptRequiredMixin, DeleteView):
    model = School
    template_name = 'schools/education_dept/school_confirm_delete.html'
    pk_url_kwarg = 'school_id'
    success_url = reverse_lazy('schools:education_dept-school-list')
    
    def delete(self, request, *args, **kwargs):
        school = self.get_object()
        log_action(request.user, 'delete', 'School', school.id, f"Deleted school: {school.name}")
        messages.success(request, _('Школа успешно удалена'))
        return super().delete(request, *args, **kwargs)

class EducationDeptUserListView(EducationDeptRequiredMixin, ListView):
    model = User
    template_name = 'schools/education_dept/user_list.html'
    context_object_name = 'users'
    
    def get_queryset(self):
        return User.objects.exclude(role='superuser').select_related().prefetch_related('schools')

class EducationDeptUserCreateView(EducationDeptRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = 'schools/education_dept/user_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        user = form.save(commit=False)
        password = form.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        else:
            import secrets
            password = secrets.token_urlsafe(8)
            user.set_password(password)
        
        user.save()
        
        log_action(self.request.user, 'create', 'User', user.id, f"Created user: {user.email}")
        messages.success(self.request, _('Пользователь успешно создан'))
        
        return redirect('schools:education_dept-user-list')

class EducationDeptUserDetailView(EducationDeptRequiredMixin, DetailView):
    model = User
    template_name = 'schools/education_dept/user_detail.html'
    context_object_name = 'target_user'
    pk_url_kwarg = 'user_id'

class EducationDeptUserUpdateView(EducationDeptRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'schools/education_dept/user_form.html'
    pk_url_kwarg = 'user_id'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context
    
    def form_valid(self, form):
        user = form.save()
        log_action(self.request.user, 'update', 'User', user.id, f"Updated user: {user.email}")
        messages.success(self.request, _('Пользователь успешно обновлен'))
        return redirect('schools:education_dept-user-detail', user_id=user.id)

class EducationDeptUserChangePasswordView(EducationDeptRequiredMixin, FormView):
    form_class = UserChangePasswordForm
    template_name = 'schools/education_dept/user_change_password.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.target_user = get_object_or_404(User, id=self.kwargs['user_id'])
        kwargs['user'] = self.target_user
        kwargs['by_admin'] = True
        return kwargs
    
    def form_valid(self, form):
        user = form.save()
        log_action(self.request.user, 'password_change', 'User', user.id, f"Changed password for user: {user.email}")
        messages.success(self.request, _('Пароль успешно изменен'))
        return redirect('schools:education_dept-user-detail', user_id=user.id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_user'] = self.target_user
        return context

class EducationDeptUserDeleteView(EducationDeptRequiredMixin, DeleteView):
    model = User
    template_name = 'schools/education_dept/user_confirm_delete.html'
    pk_url_kwarg = 'user_id'
    success_url = reverse_lazy('schools:education_dept-user-list')
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        log_action(request.user, 'delete', 'User', user.id, f"Deleted user: {user.email}")
        messages.success(request, _('Пользователь успешно удален'))
        return super().delete(request, *args, **kwargs)

class SubjectListView(EducationDeptRequiredMixin, ListView):
    model = Subject
    template_name = 'schools/education_dept/subject_list.html'
    context_object_name = 'subjects'

class SubjectCreateView(EducationDeptRequiredMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'schools/education_dept/subject_form.html'
    success_url = reverse_lazy('schools:education_dept-subject-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(self.request.user, 'create', 'Subject', self.object.id, f"Created subject: {self.object.name}")
        messages.success(self.request, _('Предмет успешно создан'))
        return response

class SubjectDeleteView(EducationDeptRequiredMixin, DeleteView):
    model = Subject
    template_name = 'schools/education_dept/subject_confirm_delete.html'
    pk_url_kwarg = 'subject_id'
    success_url = reverse_lazy('schools:education_dept-subject-list')
    
    def delete(self, request, *args, **kwargs):
        subject = self.get_object()
        log_action(request.user, 'delete', 'Subject', subject.id, f"Deleted subject: {subject.name}")
        messages.success(request, _('Предмет успешно удален'))
        return super().delete(request, *args, **kwargs)

# ==================== SCHOOL ADMIN VIEWS ====================

class SchoolAdminProfileView(SchoolAdminRequiredMixin, TemplateView):
    template_name = 'schools/school_admin/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = get_user_school(self.request.user)
        if school:
            context['school'] = school
            context['statistics'] = calculate_statistics(school)
        return context

class SchoolAdminUpdateProfileView(SchoolAdminRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'schools/school_admin/profile_form.html'
    
    def get_object(self):
        return self.request.user
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        user = form.save()
        log_action(self.request.user, 'update', 'User', user.id, "Updated own profile")
        messages.success(self.request, _('Профиль успешно обновлен'))
        return redirect('schools:school_admin-profile')

class SchoolAdminChangePasswordView(SchoolAdminRequiredMixin, FormView):
    form_class = UserChangePasswordForm
    template_name = 'schools/school_admin/change_password.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['by_admin'] = False
        return kwargs
    
    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        log_action(self.request.user, 'password_change', 'User', user.id, "Changed own password")
        messages.success(self.request, _('Пароль успешно изменен'))
        return redirect('schools:school_admin-profile')

class ClassListView(SchoolAdminRequiredMixin, ListView):
    model = ClassGroup
    template_name = 'schools/school_admin/class_list.html'
    context_object_name = 'classes'
    
    def get_queryset(self):
        school = get_user_school(self.request.user)
        return ClassGroup.objects.filter(school=school).annotate(
            student_count=Count('students'),
            average_grade=Avg('students__grades__grade', filter=Q(students__grades__quarter__in=['q1', 'q2', 'q3', 'q4']))
        )

class ClassCreateView(SchoolAdminRequiredMixin, CreateView):
    model = ClassGroup
    form_class = ClassForm
    template_name = 'schools/school_admin/class_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_user_school(self.request.user)
        return kwargs
    
    def form_valid(self, form):
        class_group = form.save(commit=False)
        class_group.school = get_user_school(self.request.user)
        class_group.save()
        
        log_action(self.request.user, 'create', 'ClassGroup', class_group.id, f"Created class: {class_group.name}")
        messages.success(self.request, _('Класс успешно создан'))
        
        return redirect('schools:school_admin-class-list')

class ClassDetailView(SchoolAdminRequiredMixin, DetailView):
    model = ClassGroup
    template_name = 'schools/school_admin/class_detail.html'
    context_object_name = 'class_obj'
    pk_url_kwarg = 'class_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_obj = self.object
        
        students = class_obj.students.annotate(
            average_grade=Avg('grades__grade', filter=Q(grades__quarter__in=['q1', 'q2', 'q3', 'q4']))
        )
        context['students'] = students
        
        subject_assignments = get_class_subject_groups(class_obj)
        context['subject_assignments'] = subject_assignments
        
        return context

class ClassUpdateView(SchoolAdminRequiredMixin, UpdateView):
    model = ClassGroup
    form_class = ClassForm
    template_name = 'schools/school_admin/class_form.html'
    pk_url_kwarg = 'class_id'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_user_school(self.request.user)
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context
    
    def form_valid(self, form):
        class_group = form.save()
        log_action(self.request.user, 'update', 'ClassGroup', class_group.id, f"Updated class: {class_group.name}")
        messages.success(self.request, _('Класс успешно обновлен'))
        return redirect('schools:school_admin-class-detail', class_id=class_group.id)

class ClassDeleteView(SchoolAdminRequiredMixin, DeleteView):
    model = ClassGroup
    template_name = 'schools/school_admin/class_confirm_delete.html'
    pk_url_kwarg = 'class_id'
    success_url = reverse_lazy('schools:school_admin-class-list')
    
    def delete(self, request, *args, **kwargs):
        class_group = self.get_object()
        log_action(request.user, 'delete', 'ClassGroup', class_group.id, f"Deleted class: {class_group.name}")
        messages.success(request, _('Класс успешно удален'))
        return super().delete(request, *args, **kwargs)

class StudentListView(SchoolAdminRequiredMixin, ListView):
    model = Student
    template_name = 'schools/school_admin/student_list.html'
    context_object_name = 'students'
    
    def get_queryset(self):
        school = get_user_school(self.request.user)
        query = self.request.GET.get('q', '')
        class_filter = self.request.GET.get('class', '')
        
        students = Student.objects.filter(class_group__school=school).select_related('class_group')
        
        if query:
            students = students.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(patronymic__icontains=query)
            )
        
        if class_filter:
            students = students.filter(class_group_id=class_filter)
        
        return students
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = get_user_school(self.request.user)
        context['classes'] = ClassGroup.objects.filter(school=school)
        context['current_class'] = self.request.GET.get('class', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context

class StudentCreateView(SchoolAdminRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'schools/school_admin/student_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_user_school(self.request.user)
        return kwargs
    
    def form_valid(self, form):
        student = form.save()
        log_action(self.request.user, 'create', 'Student', student.id, f"Created student: {student.get_full_name()}")
        messages.success(self.request, _('Учащийся успешно добавлен'))
        return redirect('schools:school_admin-student-list')

class StudentDetailView(SchoolAdminRequiredMixin, DetailView):
    model = Student
    template_name = 'schools/school_admin/student_detail.html'
    context_object_name = 'student'
    pk_url_kwarg = 'student_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        
        quarters = ['q1', 'q2', 'q3', 'q4', 'exam', 'year', 'final']
        grades_data = {}
        
        class_subjects = ClassSubjectGroup.objects.filter(
            class_group=student.class_group
        ).select_related('subject').distinct('subject')
        
        for subject in [cs.subject for cs in class_subjects]:
            subject_grades = {}
            for quarter in quarters:
                try:
                    grade = Grade.objects.get(student=student, subject=subject, quarter=quarter)
                    subject_grades[quarter] = grade.grade
                except Grade.DoesNotExist:
                    subject_grades[quarter] = None
            
            # Рассчитываем средний балл по четвертям
            quarter_averages = []
            for quarter in ['q1', 'q2', 'q3', 'q4']:
                grades_in_quarter = [g for g in subject_grades.values() if g is not None and g in range(1, 11)]
                if grades_in_quarter:
                    avg = sum(grades_in_quarter) / len(grades_in_quarter)
                    quarter_averages.append(avg)
            
            if quarter_averages:
                subject_grades['quarter_avg'] = round(sum(quarter_averages) / len(quarter_averages), 2)
            else:
                subject_grades['quarter_avg'] = None
            
            grades_data[subject] = subject_grades
        
        context['grades_data'] = grades_data
        context['quarters'] = quarters
        
        return context

class StudentUpdateView(SchoolAdminRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'schools/school_admin/student_form.html'
    pk_url_kwarg = 'student_id'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_user_school(self.request.user)
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context
    
    def form_valid(self, form):
        student = form.save()
        log_action(self.request.user, 'update', 'Student', student.id, f"Updated student: {student.get_full_name()}")
        messages.success(self.request, _('Информация об учащемся обновлена'))
        return redirect('schools:school_admin-student-detail', student_id=student.id)

class StudentDeleteView(SchoolAdminRequiredMixin, DeleteView):
    model = Student
    template_name = 'schools/school_admin/student_confirm_delete.html'
    pk_url_kwarg = 'student_id'
    success_url = reverse_lazy('schools:school_admin-student-list')
    
    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        log_action(request.user, 'delete', 'Student', student.id, f"Deleted student: {student.get_full_name()}")
        messages.success(request, _('Учащийся успешно удален'))
        return super().delete(request, *args, **kwargs)

class AddStudentToClassView(SchoolAdminRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'schools/school_admin/add_student_to_class.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_user_school(self.request.user)
        class_id = self.kwargs.get('class_id')
        if class_id:
            kwargs['initial'] = {'class_group': class_id}
        return kwargs
    
    def form_valid(self, form):
        student = form.save()
        log_action(self.request.user, 'create', 'Student', student.id, f"Added student to class: {student.get_full_name()}")
        messages.success(self.request, _('Учащийся успешно добавлен в класс'))
        return redirect('schools:school_admin-class-detail', class_id=student.class_group_id)

class TeacherListView(SchoolAdminRequiredMixin, ListView):
    model = Teacher
    template_name = 'schools/school_admin/teacher_list.html'
    context_object_name = 'teachers'
    
    def get_queryset(self):
        school = get_user_school(self.request.user)
        return Teacher.objects.filter(school=school)

class TeacherCreateView(SchoolAdminRequiredMixin, CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'schools/school_admin/teacher_form.html'
    
    def form_valid(self, form):
        teacher = form.save(commit=False)
        teacher.school = get_user_school(self.request.user)
        teacher.save()
        
        log_action(self.request.user, 'create', 'Teacher', teacher.id, f"Created teacher: {teacher.get_full_name()}")
        messages.success(self.request, _('Учитель успешно добавлен'))
        
        return redirect('schools:school_admin-teacher-list')

class TeacherDetailView(SchoolAdminRequiredMixin, DetailView):
    model = Teacher
    template_name = 'schools/school_admin/teacher_detail.html'
    context_object_name = 'teacher'
    pk_url_kwarg = 'teacher_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.object
        
        assignments = get_teacher_assignments(teacher)
        context['assignments'] = assignments
        
        return context

class TeacherUpdateView(SchoolAdminRequiredMixin, UpdateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'schools/school_admin/teacher_form.html'
    pk_url_kwarg = 'teacher_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context
    
    def form_valid(self, form):
        teacher = form.save()
        log_action(self.request.user, 'update', 'Teacher', teacher.id, f"Updated teacher: {teacher.get_full_name()}")
        messages.success(self.request, _('Информация об учителе обновлена'))
        return redirect('schools:school_admin-teacher-detail', teacher_id=teacher.id)

class TeacherDeleteView(SchoolAdminRequiredMixin, DeleteView):
    model = Teacher
    template_name = 'schools/school_admin/teacher_confirm_delete.html'
    pk_url_kwarg = 'teacher_id'
    success_url = reverse_lazy('schools:school_admin-teacher-list')
    
    def delete(self, request, *args, **kwargs):
        teacher = self.get_object()
        log_action(request.user, 'delete', 'Teacher', teacher.id, f"Deleted teacher: {teacher.get_full_name()}")
        messages.success(request, _('Учитель успешно удален'))
        return super().delete(request, *args, **kwargs)

class AssignTeacherToSubjectView(SchoolAdminRequiredMixin, FormView):
    form_class = AssignTeacherToSubjectForm
    template_name = 'schools/school_admin/assign_teacher_to_subject.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_user_school(self.request.user)
        kwargs['class_group'] = get_object_or_404(ClassGroup, id=self.kwargs['class_id'])
        return kwargs
    
    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        teacher = form.cleaned_data['teacher']
        level = form.cleaned_data['level']
        class_group = get_object_or_404(ClassGroup, id=self.kwargs['class_id'])
        
        existing_assignments = ClassSubjectGroup.objects.filter(
            class_group=class_group,
            subject=subject
        )
        
        group_number = 1
        if existing_assignments.count() == 1:
            # Уже есть один учитель, создаем вторую группу
            group_number = 2
        elif existing_assignments.count() >= 2:
            # Несколько учителей, нужно распределение по подгруппам
            messages.warning(self.request, _('Этот предмет уже имеет несколько учителей. Используйте распределение по подгруппам.'))
            return redirect('schools:school_admin-class-detail', class_id=class_group.id)
        
        assignment = ClassSubjectGroup.objects.create(
            class_group=class_group,
            subject=subject,
            teacher=teacher,
            level=level,
            group_number=group_number
        )
        
        # Если это единственная группа, добавляем всех студентов
        if group_number == 1:
            students = class_group.students.all()
            for student in students:
                StudentSubjectGroup.objects.create(
                    student=student,
                    subject_group=assignment
                )
        
        log_action(self.request.user, 'create', 'ClassSubjectGroup', assignment.id, 
                  f"Assigned teacher {teacher.get_full_name()} to subject {subject.name} in class {class_group.name}")
        messages.success(self.request, _('Учитель успешно назначен на предмет'))
        
        return redirect('schools:school_admin-class-detail', class_id=class_group.id)

class AssignTeacherToGroupView(SchoolAdminRequiredMixin, FormView):
    form_class = AssignTeacherToGroupForm
    template_name = 'schools/school_admin/assign_teacher_to_group.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_user_school(self.request.user)
        kwargs['teacher'] = get_object_or_404(Teacher, id=self.kwargs['teacher_id'])
        return kwargs
    
    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        class_groups = form.cleaned_data['class_groups']
        level = form.cleaned_data['level']
        teacher = get_object_or_404(Teacher, id=self.kwargs['teacher_id'])
        
        for class_group in class_groups:
            ClassSubjectGroup.objects.create(
                class_group=class_group,
                subject=subject,
                teacher=teacher,
                level=level,
                group_number=1
            )
        
        log_action(self.request.user, 'create', 'ClassSubjectGroup', None, 
                  f"Assigned teacher {teacher.get_full_name()} to multiple classes")
        messages.success(self.request, _('Учитель успешно назначен на классы'))
        
        return redirect('schools:school_admin-teacher-detail', teacher_id=teacher.id)

class DeleteAssignmentView(SchoolAdminRequiredMixin, DeleteView):
    model = ClassSubjectGroup
    template_name = 'schools/school_admin/assignment_confirm_delete.html'
    pk_url_kwarg = 'assignment_id'
    
    def get_success_url(self):
        return reverse('schools:school_admin-class-detail', kwargs={'class_id': self.object.class_group.id})
    
    def delete(self, request, *args, **kwargs):
        assignment = self.get_object()
        
        log_action(request.user, 'delete', 'ClassSubjectGroup', assignment.id, 
                  f"Deleted assignment: {assignment}")
        messages.success(request, _('Назначение успешно удалено'))
        
        return super().delete(request, *args, **kwargs)

class DistributeStudentsToSubgroupsView(SchoolAdminRequiredMixin, FormView):
    form_class = DistributeStudentsToSubgroupsForm
    template_name = 'schools/school_admin/distribute_students.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        class_id = self.kwargs['class_id']
        class_group = get_object_or_404(ClassGroup, id=class_id)
        
        subject_id = self.kwargs['subject_id']
        subject = get_object_or_404(Subject, id=subject_id)
        
        assignments = ClassSubjectGroup.objects.filter(
            class_group=class_group,
            subject=subject
        ).select_related('teacher')
        
        students = class_group.students.all()
        current_distribution = {}
        
        for i, assignment in enumerate(assignments):
            student_groups = StudentSubjectGroup.objects.filter(subject_group=assignment)
            current_distribution[i+1] = [sg.student for sg in student_groups]
        
        kwargs['students'] = students
        kwargs['teachers'] = [a.teacher for a in assignments]
        kwargs['current_distribution'] = current_distribution
        return kwargs
    
    def form_valid(self, form):
        class_id = self.kwargs['class_id']
        subject_id = self.kwargs['subject_id']
        
        class_group = get_object_or_404(ClassGroup, id=class_id)
        subject = get_object_or_404(Subject, id=subject_id)
        
        assignments = ClassSubjectGroup.objects.filter(
            class_group=class_group,
            subject=subject
        )
        
        with transaction.atomic():
            # Удаляем старое распределение
            StudentSubjectGroup.objects.filter(
                subject_group__in=assignments
            ).delete()
            
            # Создаем новое распределение
            for i, assignment in enumerate(assignments):
                field_name = f'group_{i+1}_students'
                students = form.cleaned_data.get(field_name, [])
                
                for student in students:
                    StudentSubjectGroup.objects.create(
                        student=student,
                        subject_group=assignment
                    )
        
        log_action(self.request.user, 'update', 'StudentSubjectGroup', None, 
                  f"Redistributed students for subject {subject.name} in class {class_group.name}")
        messages.success(self.request, _('Распределение учащихся по подгруппам успешно сохранено'))
        
        return redirect('schools:school_admin-class-detail', class_id=class_group.id)

class GradeJournalView(SchoolAdminRequiredMixin, FormView):
    form_class = GradeJournalForm
    template_name = 'schools/school_admin/grade_journal.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        class_id = self.kwargs['class_id']
        class_group = get_object_or_404(ClassGroup, id=class_id)
        
        students = class_group.students.all()
        
        subject_assignments = ClassSubjectGroup.objects.filter(
            class_group=class_group
        ).select_related('subject')
        
        # Get unique subjects
        subjects_seen = set()
        subjects = []
        for sa in subject_assignments:
            if sa.subject_id not in subjects_seen:
                subjects.append(sa.subject)
                subjects_seen.add(sa.subject_id)
        
        grades_data = {}
        grades = Grade.objects.filter(
            student__in=students,
            subject__in=subjects
        )
        
        for grade in grades:
            grades_data[(grade.student_id, grade.subject_id, grade.quarter)] = grade.grade
        
        kwargs['class_group'] = class_group
        kwargs['students'] = students
        kwargs['subjects'] = subjects
        kwargs['grades_data'] = grades_data
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs['class_id']
        class_group = get_object_or_404(ClassGroup, id=class_id)
        context['school_class'] = class_group
        
        students = class_group.students.all()
        context['students'] = students
        
        subject_assignments = ClassSubjectGroup.objects.filter(
            class_group=class_group
        ).select_related('subject')
        
        subjects_seen = set()
        subjects = []
        for sa in subject_assignments:
            if sa.subject_id not in subjects_seen:
                subjects.append(sa.subject)
                subjects_seen.add(sa.subject_id)
        context['subjects'] = subjects
        
        # Organize grades for template
        grades_dict = {}
        grades = Grade.objects.filter(student__in=students, subject__in=subjects)
        for g in grades:
            if g.student_id not in grades_dict:
                grades_dict[g.student_id] = {}
            if g.subject_id not in grades_dict[g.student_id]:
                grades_dict[g.student_id][g.subject_id] = {}
            
            # Map database quarter codes to template keys
            q_map = {'q1': 'q1', 'q2': 'q2', 'q3': 'q3', 'q4': 'q4', 'exam': 'exam', 'year': 'year', 'final': 'final'}
            grades_dict[g.student_id][g.subject_id][q_map.get(g.quarter)] = g.grade
            
        context['grades'] = grades_dict
        return context
    
    def post(self, request, *args, **kwargs):
        class_id = self.kwargs['class_id']
        class_group = get_object_or_404(ClassGroup, id=class_id)
        
        students = class_group.students.all()
        
        subject_assignments = ClassSubjectGroup.objects.filter(
            class_group=class_group
        ).select_related('subject').distinct('subject')
        
        subjects = [sa.subject for sa in subject_assignments]
        quarters = ['q1', 'q2', 'q3', 'q4', 'exam', 'year', 'final']
        
        grades_updated = 0
        grades_created = 0
        
        with transaction.atomic():
            for student in students:
                for subject in subjects:
                    for quarter in quarters:
                        field_name = f'grade_{student.id}_{subject.id}_{quarter}'
                        grade_value = request.POST.get(field_name)
                        
                        if grade_value in [None, '']:
                            grade_value = None
                        else:
                            try:
                                grade_value = int(grade_value)
                                if not (1 <= grade_value <= 10):
                                    messages.error(request, _('Оценка должна быть от 1 до 10'))
                                    return self.form_invalid(self.get_form())
                            except ValueError:
                                grade_value = None
                        
                        grade_obj, created = Grade.objects.update_or_create(
                            student=student,
                            subject=subject,
                            quarter=quarter,
                            defaults={'grade': grade_value}
                        )
                        
                        if created:
                            grades_created += 1
                        else:
                            grades_updated += 1
        
        log_action(request.user, 'update', 'Grade', None, 
                  f"Updated {grades_updated} and created {grades_created} grades for class {class_group.name}")
        messages.success(request, _('Оценки успешно сохранены'))
        
        return redirect('schools:school_admin-grade-journal', class_id=class_group.id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_group'] = get_object_or_404(ClassGroup, id=self.kwargs['class_id'])
        return context