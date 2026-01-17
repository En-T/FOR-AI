from django.urls import path, include
from . import views

app_name = 'schools'

# SUPERUSER URLS
superuser_patterns = [
    path('', views.SuperuserDashboardView.as_view(), name='superuser-dashboard'),
    path('users/', views.SuperuserUserListView.as_view(), name='superuser-user-list'),
    path('users/add/', views.SuperuserAddUserView.as_view(), name='superuser-user-add'),
    path('logs/', views.SuperuserViewLogsView.as_view(), name='superuser-logs'),
]

# EDUCATION DEPARTMENT URLS
education_dept_patterns = [
    path('', views.EducationDeptDashboardView.as_view(), name='education_dept-dashboard'),
    
    # Schools
    path('schools/', views.SchoolListView.as_view(), name='education_dept-school-list'),
    path('schools/add/', views.SchoolCreateView.as_view(), name='education_dept-school-create'),
    path('schools/<int:school_id>/', views.SchoolDetailView.as_view(), name='education_dept-school-detail'),
    path('schools/<int:school_id>/update/', views.SchoolUpdateView.as_view(), name='education_dept-school-update'),
    path('schools/<int:school_id>/delete/', views.SchoolDeleteView.as_view(), name='education_dept-school-delete'),
    
    # Users
    path('users/', views.EducationDeptUserListView.as_view(), name='education_dept-user-list'),
    path('users/add/', views.EducationDeptUserCreateView.as_view(), name='education_dept-user-create'),
    path('users/<int:user_id>/', views.EducationDeptUserDetailView.as_view(), name='education_dept-user-detail'),
    path('users/<int:user_id>/update/', views.EducationDeptUserUpdateView.as_view(), name='education_dept-user-update'),
    path('users/<int:user_id>/change-password/', views.EducationDeptUserChangePasswordView.as_view(), name='education_dept-user-change-password'),
    path('users/<int:user_id>/delete/', views.EducationDeptUserDeleteView.as_view(), name='education_dept-user-delete'),
    
    # Subjects
    path('subjects/', views.SubjectListView.as_view(), name='education_dept-subject-list'),
    path('subjects/add/', views.SubjectCreateView.as_view(), name='education_dept-subject-create'),
    path('subjects/<int:subject_id>/delete/', views.SubjectDeleteView.as_view(), name='education_dept-subject-delete'),
]

# SCHOOL ADMIN URLS
school_admin_patterns = [
    path('', views.SchoolAdminProfileView.as_view(), name='school_admin-profile'),
    path('profile/update/', views.SchoolAdminUpdateProfileView.as_view(), name='school_admin-profile-update'),
    path('change-password/', views.SchoolAdminChangePasswordView.as_view(), name='school_admin-change-password'),
    
    # Classes
    path('classes/', views.ClassListView.as_view(), name='school_admin-class-list'),
    path('classes/add/', views.ClassCreateView.as_view(), name='school_admin-class-create'),
    path('classes/<int:class_id>/', views.ClassDetailView.as_view(), name='school_admin-class-detail'),
    path('classes/<int:class_id>/update/', views.ClassUpdateView.as_view(), name='school_admin-class-update'),
    path('classes/<int:class_id>/delete/', views.ClassDeleteView.as_view(), name='school_admin-class-delete'),
    
    # Students
    path('students/', views.StudentListView.as_view(), name='school_admin-student-list'),
    path('students/add/', views.StudentCreateView.as_view(), name='school_admin-student-create'),
    path('students/<int:student_id>/', views.StudentDetailView.as_view(), name='school_admin-student-detail'),
    path('students/<int:student_id>/update/', views.StudentUpdateView.as_view(), name='school_admin-student-update'),
    path('students/<int:student_id>/delete/', views.StudentDeleteView.as_view(), name='school_admin-student-delete'),
    path('classes/<int:class_id>/students/add/', views.AddStudentToClassView.as_view(), name='school_admin-add-student-to-class'),
    
    # Teachers
    path('teachers/', views.TeacherListView.as_view(), name='school_admin-teacher-list'),
    path('teachers/add/', views.TeacherCreateView.as_view(), name='school_admin-teacher-create'),
    path('teachers/<int:teacher_id>/', views.TeacherDetailView.as_view(), name='school_admin-teacher-detail'),
    path('teachers/<int:teacher_id>/update/', views.TeacherUpdateView.as_view(), name='school_admin-teacher-update'),
    path('teachers/<int:teacher_id>/delete/', views.TeacherDeleteView.as_view(), name='school_admin-teacher-delete'),
    
    # Teacher Assignments
    path('classes/<int:class_id>/assign-teacher/', views.AssignTeacherToSubjectView.as_view(), name='school_admin-assign-teacher-to-subject'),
    path('teachers/<int:teacher_id>/assign/', views.AssignTeacherToGroupView.as_view(), name='school_admin-assign-teacher-to-group'),
    path('assignments/<int:assignment_id>/delete/', views.DeleteAssignmentView.as_view(), name='school_admin-delete-assignment'),
    
    # Student Distribution
    path('classes/<int:class_id>/distribute/<int:subject_id>/', views.DistributeStudentsToSubgroupsView.as_view(), name='school_admin-distribute-students'),
    
    # Grade Journal
    path('classes/<int:class_id>/journal/', views.GradeJournalView.as_view(), name='school_admin-grade-journal'),
]

# MAIN URL PATTERNS
urlpatterns = [
    # Superuser URLs
    path('superuser/', include(superuser_patterns)),
    
    # Education Department URLs
    path('education-dept/', include(education_dept_patterns)),
    
    # School Admin URLs
    path('school-admin/', include(school_admin_patterns)),
]