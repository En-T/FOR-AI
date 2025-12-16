from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('school-admin-only/', views.school_admin_required, name='school_admin_only'),
    path('education-dept-only/', views.education_dept_required, name='education_dept_only'),
]