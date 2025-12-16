"""
Education App URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path('health/', views.health_check_view, name='health'),
    
    # Course endpoints
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('courses/create/', views.CourseCreateView.as_view(), name='course-create'),
    path('courses/<int:course_id>/lessons/', views.LessonListView.as_view(), name='lesson-list'),
    path('courses/popular/', views.PopularCoursesView.as_view(), name='popular-courses'),
    
    # Student endpoints
    path('enroll/<int:course_id>/', views.StudentEnrollView.as_view(), name='student-enroll'),
    path('progress/', views.StudentProgressView.as_view(), name='student-progress'),
    path('progress/<int:course_id>/', views.StudentProgressView.as_view(), name='student-progress-course'),
    
    # Analytics
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
]