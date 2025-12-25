from django.contrib import admin
from .models import (
    User, School, Subject, Teacher, Class,
    Subgroup, Student, StudentSubgroupAssignment,
    TeacherAssignment, Grade
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active')
    search_fields = ('username',)
    readonly_fields = ('id', 'created_at')


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'director', 'graduating_class', 'location', 'created_by', 'created_at')
    list_filter = ('graduating_class',)
    search_fields = ('name', 'director', 'location')
    readonly_fields = ('id', 'created_at')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'school', 'created_at')
    list_filter = ('school',)
    search_fields = ('full_name',)
    readonly_fields = ('id', 'created_at')


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'school', 'created_at')
    list_filter = ('school',)
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at')


@admin.register(Subgroup)
class SubgroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'school_class', 'subject', 'created_at')
    list_filter = ('subject',)
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'school_class', 'created_at')
    list_filter = ('school_class',)
    search_fields = ('full_name',)
    readonly_fields = ('id', 'created_at')


@admin.register(StudentSubgroupAssignment)
class StudentSubgroupAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'subgroup', 'assigned_at')
    list_filter = ('subgroup',)
    search_fields = ('student__full_name',)
    readonly_fields = ('id', 'assigned_at')


@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'teacher', 'subgroup', 'assigned_at')
    list_filter = ('teacher__school',)
    search_fields = ('teacher__full_name',)
    readonly_fields = ('id', 'assigned_at')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'subject', 'quarter', 'grade', 'assigned_by', 'assigned_at', 'updated_at')
    list_filter = ('quarter', 'subject')
    search_fields = ('student__full_name',)
    readonly_fields = ('id', 'assigned_at', 'updated_at')
