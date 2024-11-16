from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("booking_portal.urls")),
    path("admin/", admin.site.urls),
    path("auth/", include("auth.urls")),
]
