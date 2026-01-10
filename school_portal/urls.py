from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("dj-admin/", admin.site.urls),
    path("", include("school_admin.urls")),
    path("", include("django.contrib.auth.urls")),
]
