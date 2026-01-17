from django.contrib import admin

from core.models import (
    AuditLog,
    Class,
    ClassSubjectGroup,
    Grade,
    School,
    Student,
    StudentSubjectGroup,
    Subject,
    Teacher,
    UserProfile,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "school", "created_at"]
    list_filter = ["role"]
    search_fields = ["user__username", "user__email"]
    raw_id_fields = ["user", "school"]


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["name", "director", "graduation_class", "location", "created_at"]
    list_filter = ["graduation_class"]
    search_fields = ["name", "director", "location"]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "graduation_class", "created_at"]
    list_filter = ["school", "graduation_class"]
    search_fields = ["name", "school__name"]
    raw_id_fields = ["school"]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["last_name", "first_name", "patronymic", "student_class", "created_at"]
    list_filter = ["student_class__school"]
    search_fields = ["last_name", "first_name", "patronymic"]
    raw_id_fields = ["student_class"]


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ["last_name", "first_name", "patronymic", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["last_name", "first_name", "patronymic"]
    raw_id_fields = ["school"]


@admin.register(ClassSubjectGroup)
class ClassSubjectGroupAdmin(admin.ModelAdmin):
    list_display = ["class_obj", "subject", "level", "group_number", "created_at"]
    list_filter = ["level", "class_obj__school"]
    search_fields = ["subject__name", "class_obj__name"]
    raw_id_fields = ["class_obj", "subject"]
    filter_horizontal = ["teachers"]


@admin.register(StudentSubjectGroup)
class StudentSubjectGroupAdmin(admin.ModelAdmin):
    list_display = ["student", "subject_group", "created_at"]
    search_fields = ["student__last_name", "student__first_name"]
    raw_id_fields = ["student", "subject_group"]


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ["student", "subject", "quarter", "grade", "created_at"]
    list_filter = ["quarter", "subject"]
    search_fields = ["student__last_name", "student__first_name"]
    raw_id_fields = ["student", "subject"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "model_name", "object_id", "timestamp"]
    list_filter = ["action", "model_name", "timestamp"]
    search_fields = ["user__username", "model_name"]
    readonly_fields = ["user", "action", "model_name", "object_id", "timestamp", "details"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
