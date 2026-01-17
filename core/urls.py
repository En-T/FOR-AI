from django.urls import path

from core.views import DashboardView, LoginView, LogoutView

app_name = "core"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("", DashboardView.as_view(), name="index"),
]
