from django.urls import path
from .views import (
    PackageCreateView, PackageListView, PackageDetailView, GenerateTransactionView, PurchasePackageView,
    CancelTransactionView, UserPurchaseHistoryView
)

urlpatterns = [
    path('package/', PackageCreateView.as_view(), name='package-create'),
    path('packages/', PackageListView.as_view(), name='package-list'),
    path('packages/<int:package_id>/', PackageDetailView.as_view(), name='package-detail'),
    path('packages/<int:package_id>/generate-transaction/', GenerateTransactionView.as_view(), name='generate-transaction'),
    path('transactions/<str:transaction_id>/purchase/', PurchasePackageView.as_view(), name='purchase-package'),
    path('transactions/<str:transaction_id>/cancel/', CancelTransactionView.as_view(), name='cancel-transaction'),
    path('customer/purchase-history/', UserPurchaseHistoryView.as_view(), name='user-purchase-history'),
]
