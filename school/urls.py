from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
    )

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    path("api/v1/auth/", include('djoser.urls')),
    path("api/v1/auth/", include('core_apps.user_auth.urls')),
    path("api/v1/teacher/", include('core_apps.teacher_profile.urls')),
    path("api/v1/parent/", include('core_apps.parent_profile.urls')),
]

admin.site.site_header = "Outshine International School Admin"
admin.site.site_title = "Outshine International School Admin Portal"
admin.site.index_title = "Welcome to Outshine International School Admin Portal"