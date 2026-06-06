"""Dashboard URL configuration for the DevOps cockpit API."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from dashboard import views

router = DefaultRouter()
router.register(r'organizations', views.OrganizationViewSet, basename='organization')
router.register(r'repositories', views.RepositoryViewSet, basename='repository')
router.register(r'connections', views.RepoConnectionViewSet, basename='repoconnection')
router.register(r'snapshots', views.RepoMetricSnapshotViewSet, basename='snapshot')
router.register(r'digests', views.RepoDigestViewSet, basename='digest')

app_name = 'dashboard'

urlpatterns = [
    path('', include(router.urls)),
    path('fleet/overview/', views.FleetOverviewView.as_view(), name='fleet-overview'),
    path('fleet/attention/', views.fleet_attention, name='fleet-attention'),
    path('fleet/digest/', views.generate_fleet_digest_view, name='fleet-digest'),
]
