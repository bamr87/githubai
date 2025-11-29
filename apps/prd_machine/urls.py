"""PRD MACHINE URL configuration."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from prd_machine import views

router = DefaultRouter()
router.register(r'prd-states', views.PRDStateViewSet, basename='prd-state')
router.register(r'prd-versions', views.PRDVersionViewSet, basename='prd-version')
router.register(r'prd-conflicts', views.PRDConflictViewSet, basename='prd-conflict')
router.register(r'prd-events', views.PRDEventViewSet, basename='prd-event')

urlpatterns = [
    path('', include(router.urls)),
    # Webhook endpoint for GitHub events
    path('webhook/github/', views.github_webhook, name='prd-github-webhook'),
    # Manual trigger endpoints
    path('sync/<str:repo>/', views.sync_prd, name='prd-sync'),
    path('distill/<str:repo>/', views.distill_prd, name='prd-distill'),
    path('generate/<str:repo>/', views.generate_prd, name='prd-generate'),
    path('detect-conflicts/<str:repo>/', views.detect_conflicts, name='prd-detect-conflicts'),
    path('export-issues/<str:repo>/', views.export_to_issues, name='prd-export-issues'),
]

app_name = 'prd_machine'
