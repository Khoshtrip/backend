from django.urls import path
from .views import (
    PackageCreateView
)

urlpatterns = [
    path('packages/', PackageCreateView.as_view(), name='package-create'),
]
