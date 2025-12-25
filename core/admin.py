from django.contrib import admin
from .models import (
    User, School, Subject, Teacher, Class, 
    Subgroup, Student, StudentSubgroupAssignment, 
    TeacherAssignment, Grade
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('username', 'email')
    readonly_fields = ('id', 'created_at', 'last_login', 'date_joined')


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'director', 'graduating_class', 'location', 'created_at')
    list_filter = ('graduating_class', 'created_at')
    search_fields = ('name', 'director', 'location')
    readonly_fields = ('id', 'created_at')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'school', 'created_at')
    list_filter = ('school', 'created_at')
    search_fields = ('full_name', 'school__name')
    readonly_fields = ('id', 'created_at')


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'created_at')
    list_filter = ('school', 'created_at')
    search_fields = ('name', 'school__name')
    readonly_fields = ('id', 'created_at')


@admin.register(Subgroup)
class SubgroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_obj', 'subject', 'created_at')
    list_filter = ('class_obj__school', 'subject', 'created_at')
    search_fields = ('name', 'class_obj__name', 'subject__name')
    readonly_fields = ('id', 'created_at')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'class_obj', 'created_at')
    list_filter = ('class_obj__school', 'class_obj', 'created_at')
    search_fields = ('full_name', 'class_obj__name')
    readonly_fields = ('id', 'created_at')


@admin.register(StudentSubgroupAssignment)
class StudentSubgroupAssignmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'subgroup', 'assigned_at')
    list_filter = ('subgroup__class_obj__school', 'subgroup__subject', 'assigned_at')
    search_fields = ('student__full_name', 'subgroup__name')
    readonly_fields = ('id', 'assigned_at')


@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subgroup', 'assigned_at')
    list_filter = ('teacher__school', 'subgroup__subject', 'assigned_at')
    search_fields = ('teacher__full_name', 'subgroup__name')
    readonly_fields = ('id', 'assigned_at')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'quarter', 'grade', 'assigned_by', 'assigned_at', 'updated_at')
    list_filter = ('quarter', 'subject', 'assigned_by', 'assigned_at')
    search_fields = ('student__full_name', 'subject__name')
    readonly_fields = ('id', 'assigned_at', 'updated_at')
