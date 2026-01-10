from django.urls import path

from . import views

app_name = "school_admin"

urlpatterns = [
    path("admin/", views.SchoolAdminDashboardView.as_view(), name="dashboard"),
    path("admin/report/", views.SchoolAdminReportView.as_view(), name="report"),
    path("admin/profile/", views.SchoolAdminProfileView.as_view(), name="profile"),
    path("admin/profile/edit/", views.SchoolAdminProfileUpdateView.as_view(), name="profile_edit"),
    path("admin/profile/password/", views.SchoolAdminPasswordChangeView.as_view(), name="password_change"),
    path("admin/classes/", views.ClassListView.as_view(), name="class_list"),
    path("admin/classes/create/", views.ClassCreateView.as_view(), name="class_create"),
    path("admin/classes/<int:pk>/", views.ClassDetailView.as_view(), name="class_detail"),
    path("admin/classes/<int:pk>/edit/", views.ClassUpdateView.as_view(), name="class_update"),
    path("admin/classes/<int:pk>/delete/", views.ClassDeleteView.as_view(), name="class_delete"),
    path("admin/classes/<int:pk>/add-student/", views.StudentCreateView.as_view(), name="class_add_student"),
    path("admin/classes/<int:pk>/gradebook/", views.GradeBookView.as_view(), name="class_gradebook"),
    path(
        "admin/classes/<int:pk>/assignments/create/",
        views.ClassTeacherAssignmentCreateView.as_view(),
        name="assignment_create",
    ),
    path(
        "admin/classes/<int:pk>/assignments/<int:assignment_id>/edit/",
        views.ClassTeacherAssignmentUpdateView.as_view(),
        name="assignment_update",
    ),
    path(
        "admin/classes/<int:pk>/assignments/<int:assignment_id>/delete/",
        views.ClassTeacherAssignmentDeleteView.as_view(),
        name="assignment_delete",
    ),
    path("admin/teachers/", views.TeacherListView.as_view(), name="teacher_list"),
    path("admin/teachers/create/", views.TeacherCreateView.as_view(), name="teacher_create"),
    path("admin/teachers/<int:pk>/", views.TeacherDetailView.as_view(), name="teacher_detail"),
    path("admin/teachers/<int:pk>/edit/", views.TeacherUpdateView.as_view(), name="teacher_update"),
    path("admin/teachers/<int:pk>/delete/", views.TeacherDeleteView.as_view(), name="teacher_delete"),
    path("admin/teachers/<int:pk>/assign/", views.TeacherAssignmentCreateView.as_view(), name="teacher_assign"),
    path("admin/students/", views.StudentListView.as_view(), name="student_list"),
    path("admin/students/<int:pk>/", views.StudentDetailView.as_view(), name="student_detail"),
    path("admin/students/<int:pk>/edit/", views.StudentUpdateView.as_view(), name="student_update"),
    path("admin/students/<int:pk>/delete/", views.StudentDeleteView.as_view(), name="student_delete"),
    path("admin/gradebook/save/", views.GradeBookSaveView.as_view(), name="gradebook_save"),
]
