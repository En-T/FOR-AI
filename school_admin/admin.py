from django.contrib import admin

from .models import (
    AuditLog,
    AssignmentStudent,
    ClassTeacherAssignment,
    Grade,
    School,
    SchoolAdminProfile,
    SchoolClass,
    Student,
    Subject,
    Teacher,
)

admin.site.register(School)
admin.site.register(SchoolAdminProfile)
admin.site.register(Subject)
admin.site.register(SchoolClass)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(ClassTeacherAssignment)
admin.site.register(AssignmentStudent)
admin.site.register(Grade)
admin.site.register(AuditLog)
