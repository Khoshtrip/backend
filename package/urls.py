from django.urls import path
from .views import (
    PackageCreateView, PackageListView
)

urlpatterns = [
    path('package/', PackageCreateView.as_view(), name='package-create'),
    path('packages/', PackageListView.as_view(), name='package-list'),
]
