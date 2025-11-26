"""Core URLs - merged from all apps"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    HealthCheckView,
    IssueTemplateViewSet,
    IssueViewSet,
    ChatView,
    AIProviderViewSet,
    AIModelViewSet,
)

router = DefaultRouter()
router.register(r"issues", IssueViewSet, basename="issue")
router.register(r"templates", IssueTemplateViewSet, basename="issuetemplate")
router.register(r"providers", AIProviderViewSet, basename="aiprovider")
router.register(r"models", AIModelViewSet, basename="aimodel")

urlpatterns = [
    path("issues/", include(router.urls)),
    path("providers/", include([
        path("", AIProviderViewSet.as_view({'get': 'list'}), name="provider-list"),
        path("<int:pk>/", AIProviderViewSet.as_view({'get': 'retrieve'}), name="provider-detail"),
    ])),
    path("models/", include([
        path("", AIModelViewSet.as_view({'get': 'list'}), name="model-list"),
        path("<int:pk>/", AIModelViewSet.as_view({'get': 'retrieve'}), name="model-detail"),
        path("by-provider/<str:provider_name>/", AIModelViewSet.as_view({'get': 'by_provider'}), name="models-by-provider"),
    ])),
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("chat/", ChatView.as_view(), name="chat"),
]
