from django.contrib import admin
from .models import (
    User, School, Teacher, Subject, Class, Subgroup,
    Student, StudentSubgroupAssignment, TeacherAssignment, Grade
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active')
    search_fields = ('username',)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'director', 'graduating_class', 'location', 'created_by')
    list_filter = ('location',)
    search_fields = ('name', 'director')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'school', 'created_at')
    list_filter = ('school',)
    search_fields = ('full_name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'created_at')
    list_filter = ('school',)
    search_fields = ('name',)


@admin.register(Subgroup)
class SubgroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_obj', 'subject', 'created_at')
    list_filter = ('subject',)
    search_fields = ('name',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'class_obj', 'created_at')
    list_filter = ('class_obj',)
    search_fields = ('full_name',)


@admin.register(StudentSubgroupAssignment)
class StudentSubgroupAssignmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'subgroup', 'assigned_at')
    list_filter = ('subgroup',)


@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subgroup', 'assigned_at')
    list_filter = ('subgroup',)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'quarter', 'grade', 'assigned_by', 'assigned_at')
    list_filter = ('quarter', 'subject')
    search_fields = ('student__full_name',)
