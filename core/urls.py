from django.urls import path
from . import views
from . import views_auth, views_superuser

urlpatterns = [
    # Authentication
    path('login/', views_auth.LoginView.as_view(), name='login'),
    path('logout/', views_auth.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'), # Keep old register if needed, though superuser has its own

    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Superuser Routes
    path('superuser/', views_superuser.SuperuserDashboardView.as_view(), name='superuser-dashboard'),
    path('superuser/users/', views_superuser.UserListView.as_view(), name='user-list'),
    path('superuser/users/create/', views_superuser.UserCreateView.as_view(), name='user-create'),
    path('superuser/users/<int:pk>/', views_superuser.UserDetailView.as_view(), name='user-detail'),
    path('superuser/users/<int:pk>/edit/', views_superuser.UserUpdateView.as_view(), name='user-update'),
    path('superuser/users/<int:pk>/delete/', views_superuser.UserDeleteView.as_view(), name='user-delete'),
    path('superuser/users/<int:pk>/change-password/', views_superuser.UserChangePasswordView.as_view(), name='user-change-password'),
    path('superuser/statistics/', views_superuser.SchoolStatisticsView.as_view(), name='school-statistics'),
    path('superuser/logs/', views_superuser.AuditLogListView.as_view(), name='audit-logs'),
    path('superuser/logs/export/', views_superuser.export_logs_to_csv, name='export-logs'),

    # Schools (DEPT_EDUCATION)
    path('schools/', views.school_list, name='school_list'),
    path('schools/create/', views.school_create, name='school_create'),
    path('schools/<int:pk>/update/', views.school_update, name='school_update'),
    path('schools/<int:pk>/delete/', views.school_delete, name='school_delete'),

    # Classes (ADMIN_SCHOOL)
    path('classes/', views.class_list, name='class_list'),
    path('classes/create/', views.class_create, name='class_create'),
    path('classes/<int:pk>/update/', views.class_update, name='class_update'),
    path('classes/<int:pk>/delete/', views.class_delete, name='class_delete'),

    # Students (ADMIN_SCHOOL)
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:pk>/update/', views.student_update, name='student_update'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('students/bulk-upload/', views.student_bulk_upload, name='student_bulk_upload'),

    # Teachers (ADMIN_SCHOOL)
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/create/', views.teacher_create, name='teacher_create'),
    path('teachers/<int:pk>/update/', views.teacher_update, name='teacher_update'),
    path('teachers/<int:pk>/delete/', views.teacher_delete, name='teacher_delete'),

    # Subgroup Assignments (ADMIN_SCHOOL)
    path('subgroups/assignments/<int:class_id>/', views.subgroup_assignments, name='subgroup_assignments'),
    path('subgroups/<int:subgroup_id>/assign-teacher/', views.assign_teacher, name='assign_teacher'),
    path('subgroups/students/<int:class_id>/', views.assign_students_to_subgroups, name='assign_students_to_subgroups'),

    # Grades (ADMIN_SCHOOL)
    path('grades/input/<int:class_id>/', views.grade_input, name='grade_input'),
    path('grades/save/', views.grade_save, name='grade_save'),

    # Reports (ADMIN_SCHOOL)
    path('reports/student/<int:student_id>/', views.student_grades, name='student_grades'),
]
