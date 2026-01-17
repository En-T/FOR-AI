from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import School, ClassGroup, Student, Teacher, Subject, ClassSubjectGroup

class SuperuserRequiredMixin(AccessMixin):
    """Проверка доступа для суперпользователя"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class EducationDeptRequiredMixin(AccessMixin):
    """Проверка доступа для отдела образования"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'education_dept':
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class SchoolAdminRequiredMixin(AccessMixin):
    """Проверка доступа для администратора школы"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'school_admin':
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class SchoolOwnerRequiredMixin(AccessMixin):
    """Проверка, что пользователь является администратором нужной школы"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'school_admin':
            return self.handle_no_permission()
        
        school_id = self.kwargs.get('school_id')
        if school_id:
            school = get_object_or_404(School, id=school_id)
            if not self._is_school_owner(request.user, school):
                raise PermissionDenied("Вы не являетесь администратором этой школы")
        
        return super().dispatch(request, *args, **kwargs)
    
    def _is_school_owner(self, user, school):
        """Проверка, что пользователь администрирует данную школу"""
        if user.role == 'school_admin':
            try:
                return user.school == school
            except AttributeError:
                return False
        return user.is_superuser or user.role == 'education_dept'

class ClassOwnerRequiredMixin(AccessMixin):
    """Проверка доступа к классу (только для администратора школы)"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        class_id = self.kwargs.get('class_id')
        if class_id:
            class_group = get_object_or_404(ClassGroup, id=class_id)
            if not self._can_access_class(request.user, class_group):
                raise PermissionDenied("У вас нет доступа к этому классу")
        
        return super().dispatch(request, *args, **kwargs)
    
    def _can_access_class(self, user, class_group):
        """Проверка доступа к классу"""
        if user.role == 'school_admin':
            try:
                return user.owned_school == class_group.school
            except AttributeError:
                return False
        return user.is_superuser or user.role == 'education_dept'

class StudentOwnerRequiredMixin(AccessMixin):
    """Проверка доступа к учащемуся"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        student_id = self.kwargs.get('student_id')
        if student_id:
            student = get_object_or_404(Student, id=student_id)
            if not self._can_access_student(request.user, student):
                raise PermissionDenied("У вас нет доступа к этому учащемуся")
        
        return super().dispatch(request, *args, **kwargs)
    
    def _can_access_student(self, user, student):
        """Проверка доступа к учащемуся"""
        if user.role == 'school_admin':
            try:
                return user.owned_school == student.class_group.school
            except AttributeError:
                return False
        return user.is_superuser or user.role == 'education_dept'

class TeacherOwnerRequiredMixin(AccessMixin):
    """Проверка доступа к учителю"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        teacher_id = self.kwargs.get('teacher_id')
        if teacher_id:
            teacher = get_object_or_404(Teacher, id=teacher_id)
            if not self._can_access_teacher(request.user, teacher):
                raise PermissionDenied("У вас нет доступа к этому учителю")
        
        return super().dispatch(request, *args, **kwargs)
    
    def _can_access_teacher(self, user, teacher):
        """Проверка доступа к учителю"""
        if user.role == 'school_admin':
            try:
                return user.owned_school == teacher.school
            except AttributeError:
                return False
        return user.is_superuser or user.role == 'education_dept'