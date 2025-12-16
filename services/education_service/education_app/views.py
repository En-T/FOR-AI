"""
Education App Views
"""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
import json

from .models import (
    Course, Lesson, Student, Enrollment, Assessment, 
    StudentProgress, AnalyticsEvent
)
from .serializers import (
    CourseSerializer, LessonSerializer, StudentSerializer,
    EnrollmentSerializer, AssessmentSerializer,
    StudentProgressSerializer, AnalyticsEventSerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_view(request):
    """Health check endpoint for education service"""
    return Response({
        'status': 'healthy',
        'service': 'education_service',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })


class CourseListView(generics.ListAPIView):
    """List all active courses"""
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by difficulty level
        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
            
        # Search courses
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(instructor__icontains=search)
            )
            
        return queryset


class CourseDetailView(generics.RetrieveAPIView):
    """Get course details with lessons"""
    queryset = Course.objects.filter(is_active=True).prefetch_related('lessons')
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]


class CourseCreateView(generics.CreateAPIView):
    """Create new course (instructor/admin only)"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]


class LessonListView(generics.ListAPIView):
    """List lessons for a course"""
    serializer_class = LessonSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return Lesson.objects.filter(course_id=course_id, is_published=True)


class StudentEnrollView(APIView):
    """Enroll student in course"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, course_id):
        """Enroll current user in course"""
        try:
            course = Course.objects.get(id=course_id, is_active=True)
            
            # Get or create student profile
            student, created = Student.objects.get_or_create(
                user=request.user,
                defaults={
                    'date_of_birth': request.data.get('date_of_birth'),
                    'phone_number': request.data.get('phone_number', '')
                }
            )
            
            # Check if already enrolled
            if Enrollment.objects.filter(student=student, course=course).exists():
                return Response({
                    'error': 'Already enrolled in this course'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create enrollment
            enrollment = Enrollment.objects.create(
                student=student,
                course=course
            )
            
            # Log analytics event
            AnalyticsEvent.objects.create(
                student=student,
                event_type='COURSE_VIEW',
                course=course,
                metadata={'action': 'enrolled'}
            )
            
            serializer = EnrollmentSerializer(enrollment)
            return Response({
                'message': 'Successfully enrolled in course',
                'enrollment': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Course.DoesNotExist:
            return Response({
                'error': 'Course not found'
            }, status=status.HTTP_404_NOT_FOUND)


class StudentProgressView(APIView):
    """Student progress tracking"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_id=None):
        """Get student's progress"""
        try:
            student = request.user.student
            if course_id:
                enrollments = Enrollment.objects.filter(
                    student=student, 
                    course_id=course_id
                ).select_related('course')
            else:
                enrollments = Enrollment.objects.filter(student=student).select_related('course')
            
            progress_data = []
            for enrollment in enrollments:
                progress_data.append({
                    'course': {
                        'id': enrollment.course.id,
                        'title': enrollment.course.title,
                        'instructor': enrollment.course.instructor
                    },
                    'progress_percentage': enrollment.progress_percentage,
                    'is_completed': enrollment.is_completed,
                    'enrolled_at': enrollment.enrolled_at,
                    'completed_at': enrollment.completed_at
                })
            
            return Response({'progress': progress_data})
            
        except Student.DoesNotExist:
            return Response({'progress': []})


class AnalyticsView(APIView):
    """Analytics and reporting"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get learning analytics"""
        try:
            student = request.user.student
            
            # Overall progress
            total_enrollments = Enrollment.objects.filter(student=student).count()
            completed_courses = Enrollment.objects.filter(
                student=student, 
                is_completed=True
            ).count()
            
            # Recent activity (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_events = AnalyticsEvent.objects.filter(
                student=student,
                timestamp__gte=thirty_days_ago
            ).count()
            
            # Course completion rate
            if total_enrollments > 0:
                completion_rate = (completed_courses / total_enrollments) * 100
            else:
                completion_rate = 0
            
            data = {
                'total_enrollments': total_enrollments,
                'completed_courses': completed_courses,
                'completion_rate': round(completion_rate, 2),
                'recent_activity': recent_events,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return Response(data)
            
        except Student.DoesNotExist:
            return Response({
                'total_enrollments': 0,
                'completed_courses': 0,
                'completion_rate': 0,
                'recent_activity': 0,
                'message': 'Student profile not found'
            })


class PopularCoursesView(generics.ListAPIView):
    """Get most popular courses"""
    queryset = Course.objects.filter(is_active=True).annotate(
        enrollment_count=Count('enrollment')
    ).order_by('-enrollment_count')
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]