"""
Education App Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Course(models.Model):
    """Course model"""
    DIFFICULTY_LEVELS = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.CharField(max_length=100)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='BEGINNER')
    duration_hours = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Lesson model"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    video_url = models.URLField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lesson'
        ordering = ['order']
        unique_together = ['course', 'order']
        
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Student(models.Model):
    """Student model extending User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    enrolled_courses = models.ManyToManyField(Course, through='Enrollment', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student'
        
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Enrollment(models.Model):
    """Student course enrollment"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'enrollment'
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
        
    def __str__(self):
        return f"{self.student.user.username} - {self.course.title}"


class Assessment(models.Model):
    """Assessment/Quiz model"""
    ASSESSMENT_TYPES = [
        ('QUIZ', 'Quiz'),
        ('EXAM', 'Exam'),
        ('ASSIGNMENT', 'Assignment'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    total_points = models.PositiveIntegerField(default=100)
    passing_score = models.PositiveIntegerField(default=70)
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assessment'
        ordering = ['course', 'title']
        
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class StudentProgress(models.Model):
    """Track student progress in lessons"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_progress'
        unique_together = ['student', 'lesson']
        ordering = ['-completed_at', '-updated_at']
        
    def __str__(self):
        return f"{self.student.user.username} - {self.lesson.title}"


class AnalyticsEvent(models.Model):
    """Analytics events for educational activities"""
    EVENT_TYPES = [
        ('COURSE_VIEW', 'Course View'),
        ('LESSON_START', 'Lesson Start'),
        ('LESSON_COMPLETE', 'Lesson Complete'),
        ('ASSESSMENT_START', 'Assessment Start'),
        ('ASSESSMENT_COMPLETE', 'Assessment Complete'),
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_event'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['event_type', '-timestamp']),
            models.Index(fields=['student', '-timestamp']),
        ]
        
    def __str__(self):
        return f"{self.event_type} - {self.student.user.username if self.student else 'Anonymous'}"