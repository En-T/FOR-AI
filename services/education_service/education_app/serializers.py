"""
Education App Serializers
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Course, Lesson, Student, Enrollment, Assessment, 
    StudentProgress, AnalyticsEvent
)


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model"""
    lesson_count = serializers.SerializerMethodField()
    enrollment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = (
            'id', 'title', 'description', 'instructor', 'difficulty_level',
            'duration_hours', 'price', 'is_active', 'created_at', 
            'updated_at', 'lesson_count', 'enrollment_count'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'lesson_count', 'enrollment_count')
    
    def get_lesson_count(self, obj):
        return obj.lessons.filter(is_published=True).count()
    
    def get_enrollment_count(self, obj):
        return obj.enrollment_set.count()


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model"""
    
    class Meta:
        model = Lesson
        fields = (
            'id', 'course', 'title', 'content', 'video_url',
            'duration_minutes', 'order', 'is_published', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Student
        fields = (
            'id', 'user', 'user_username', 'user_email', 'full_name',
            'date_of_birth', 'phone_number', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model"""
    student_username = serializers.CharField(source='student.user.username', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = (
            'id', 'student', 'student_username', 'course', 'course_title',
            'enrolled_at', 'completed_at', 'progress_percentage', 
            'is_completed'
        )
        read_only_fields = ('id', 'enrolled_at', 'completed_at')


class AssessmentSerializer(serializers.ModelSerializer):
    """Serializer for Assessment model"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Assessment
        fields = (
            'id', 'course', 'course_title', 'title', 'description',
            'assessment_type', 'total_points', 'passing_score', 
            'time_limit_minutes', 'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class StudentProgressSerializer(serializers.ModelSerializer):
    """Serializer for StudentProgress model"""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    student_username = serializers.CharField(source='student.user.username', read_only=True)
    
    class Meta:
        model = StudentProgress
        fields = (
            'id', 'student', 'student_username', 'lesson', 'lesson_title',
            'is_completed', 'time_spent_minutes', 'completed_at',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class AnalyticsEventSerializer(serializers.ModelSerializer):
    """Serializer for AnalyticsEvent model"""
    student_username = serializers.CharField(source='student.user.username', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    assessment_title = serializers.CharField(source='assessment.title', read_only=True)
    
    class Meta:
        model = AnalyticsEvent
        fields = (
            'id', 'student', 'student_username', 'event_type',
            'course', 'course_title', 'lesson', 'lesson_title',
            'assessment', 'assessment_title', 'metadata', 'timestamp'
        )
        read_only_fields = ('id', 'timestamp')


class CourseAnalyticsSerializer(serializers.Serializer):
    """Serializer for course analytics data"""
    total_courses = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_enrollments = serializers.IntegerField()
    average_completion_rate = serializers.FloatField()
    popular_courses = CourseSerializer(many=True, read_only=True)