from django.contrib import admin
from .models import (
    School, Subject, Class, Student, Teacher,
    ClassTeacherAssignment, Subgroup, SubgroupStudent, Grade
)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'director', 'final_grade', 'location', 'created_at']
    list_filter = ['final_grade', 'created_at']
    search_fields = ['name', 'director', 'location']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


class StudentInline(admin.TabularInline):
    model = Student
    extra = 0
    fields = ['last_name', 'first_name', 'middle_name']


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'created_at']
    list_filter = ['school', 'created_at']
    search_fields = ['name', 'school__name']
    inlines = [StudentInline]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'class_ref', 'created_at']
    list_filter = ['class_ref__school', 'class_ref', 'created_at']
    search_fields = ['last_name', 'first_name', 'middle_name']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'school', 'created_at']
    list_filter = ['school', 'created_at']
    search_fields = ['last_name', 'first_name', 'middle_name']


class SubgroupInline(admin.TabularInline):
    model = Subgroup
    extra = 0
    fields = ['order']


@admin.register(ClassTeacherAssignment)
class ClassTeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ['class_ref', 'subject', 'teacher', 'study_level', 'has_subgroups']
    list_filter = ['study_level', 'has_subgroups', 'class_ref__school']
    search_fields = ['class_ref__name', 'subject__name', 'teacher__last_name']
    inlines = [SubgroupInline]


class SubgroupStudentInline(admin.TabularInline):
    model = SubgroupStudent
    extra = 0
    fields = ['student']


@admin.register(Subgroup)
class SubgroupAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'order', 'created_at']
    list_filter = ['assignment__class_ref__school', 'created_at']
    search_fields = ['assignment__subject__name', 'assignment__teacher__last_name']
    inlines = [SubgroupStudentInline]


@admin.register(SubgroupStudent)
class SubgroupStudentAdmin(admin.ModelAdmin):
    list_display = ['subgroup', 'student']
    list_filter = ['subgroup__assignment__class_ref__school']
    search_fields = ['student__last_name', 'student__first_name']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'quarter', 'grade', 'updated_at']
    list_filter = ['quarter', 'grade', 'updated_at']
    search_fields = [
        'student__last_name',
        'student__first_name',
        'assignment__subject__name'
    ]
    readonly_fields = ['created_at', 'updated_at']
