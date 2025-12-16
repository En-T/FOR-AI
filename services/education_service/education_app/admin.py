"""
Education App Admin Configuration
"""
from django.contrib import admin
from .models import (
    Course, Lesson, Student, Enrollment, Assessment,
    StudentProgress, AnalyticsEvent
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin interface for Course model"""
    list_display = ('title', 'instructor', 'difficulty_level', 'price', 'is_active', 'created_at')
    list_filter = ('difficulty_level', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'instructor')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Course Information', {
            'fields': ('title', 'description', 'instructor', 'difficulty_level')
        }),
        ('Details', {
            'fields': ('duration_hours', 'price', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin interface for Lesson model"""
    list_display = ('title', 'course', 'order', 'is_published', 'duration_minutes')
    list_filter = ('is_published', 'course', 'created_at')
    search_fields = ('title', 'content', 'course__title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('course', 'order')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Student model"""
    list_display = ('user', 'phone_number', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin interface for Enrollment model"""
    list_display = ('student', 'course', 'progress_percentage', 'is_completed', 'enrolled_at')
    list_filter = ('is_completed', 'enrolled_at', 'course')
    search_fields = ('student__user__username', 'course__title')
    readonly_fields = ('enrolled_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student__user', 'course')


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    """Admin interface for Assessment model"""
    list_display = ('title', 'course', 'assessment_type', 'total_points', 'passing_score', 'is_active')
    list_filter = ('assessment_type', 'is_active', 'course')
    search_fields = ('title', 'course__title')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course')


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    """Admin interface for StudentProgress model"""
    list_display = ('student', 'lesson', 'is_completed', 'time_spent_minutes', 'completed_at')
    list_filter = ('is_completed', 'completed_at', 'lesson__course')
    search_fields = ('student__user__username', 'lesson__title')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student__user', 'lesson', 'lesson__course')


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    """Admin interface for AnalyticsEvent model"""
    list_display = ('event_type', 'student', 'course', 'timestamp')
    list_filter = ('event_type', 'timestamp', 'course')
    search_fields = ('student__user__username', 'course__title')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student__user', 'course', 'lesson', 'assessment')