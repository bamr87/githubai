"""Core URLs - merged from all apps"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import HealthCheckView, IssueTemplateViewSet, IssueViewSet

router = DefaultRouter()
router.register(r"issues", IssueViewSet, basename="issue")
router.register(r"templates", IssueTemplateViewSet, basename="issuetemplate")

urlpatterns = [
    path("issues/", include(router.urls)),
    path("health/", HealthCheckView.as_view(), name="health-check"),
]
