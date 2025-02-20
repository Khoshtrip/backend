from django.urls import path
from .views import (
    PackageCreateView, PackageListView, PackageDetailView
)

urlpatterns = [
    path('package/', PackageCreateView.as_view(), name='package-create'),
    path('packages/', PackageListView.as_view(), name='package-list'),
    path('packages/<int:package_id>/', PackageDetailView.as_view(), name='package-detail'),
]
