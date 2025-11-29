"""
URL configuration for githubai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from core.views import HealthCheckView

# Create router for API viewsets
router = routers.DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('core.urls')),
    path('api/prd-machine/', include('prd_machine.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('health/', HealthCheckView.as_view(), name='health-check'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin customization
admin.site.site_header = "GitHubAI Administration"
admin.site.site_title = "GitHubAI Admin"
admin.site.index_title = "Welcome to GitHubAI Administration"
