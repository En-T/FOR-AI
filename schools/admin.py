from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, School, ClassGroup, Student, Teacher, Subject,
    ClassSubjectGroup, StudentSubjectGroup, Grade, AuditLog
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'patronymic')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'role', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'patronymic')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'director_name', 'graduation_class', 'education_dept', 'created_at')
    list_filter = ('graduation_class', 'created_at')
    search_fields = ('name', 'director_name')

@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'created_at')
    list_filter = ('school', 'created_at')
    search_fields = ('name', 'school__name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'class_group', 'created_at')
    list_filter = ('class_group__school', 'class_group', 'created_at')
    search_fields = ('first_name', 'last_name', 'patronymic')
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'ФИО'

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'school', 'created_at')
    list_filter = ('school', 'created_at')
    search_fields = ('first_name', 'last_name', 'patronymic')
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'ФИО'

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(ClassSubjectGroup)
class ClassSubjectGroupAdmin(admin.ModelAdmin):
    list_display = ('class_group', 'subject', 'teacher', 'level', 'group_number', 'created_at')
    list_filter = ('level', 'group_number', 'class_group__school', 'subject')
    search_fields = ('class_group__name', 'subject__name', 'teacher__first_name', 'teacher__last_name')

@admin.register(StudentSubjectGroup)
class StudentSubjectGroupAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject_group', 'created_at')
    list_filter = ('subject_group__subject', 'subject_group__class_group__school')
    search_fields = ('student__first_name', 'student__last_name', 'subject_group__subject__name')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'quarter', 'grade', 'updated_at')
    list_filter = ('quarter', 'subject', 'student__class_group__school', 'student__class_group')
    search_fields = ('student__first_name', 'student__last_name', 'subject__name')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('actor', 'action', 'model_name', 'object_id', 'created_at')
    list_filter = ('action', 'model_name', 'created_at')
    search_fields = ('actor__email', 'details', 'model_name')
    readonly_fields = ('created_at',)