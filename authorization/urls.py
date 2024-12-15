from django.urls import path
from .views import (
    SendVerificationCodeView,
    VerifyCodeView,
    RegisterBuyerView,
    RegisterProviderView,
    LoginView,
    LogoutView,
    RefreshTokenView,
    UserProfileView,
)

urlpatterns = [
    path('auth/send-verification-code/', SendVerificationCodeView.as_view(), name='send-verification-code'),
    path('auth/verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    path('auth/register/customer/', RegisterBuyerView.as_view(), name='register-buyer'),
    path('auth/register/provider/', RegisterProviderView.as_view(), name='register-provider'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', RefreshTokenView.as_view(), name='refresh-token'),
    path('auth/me/', UserProfileView.as_view(), name='user-profile'),
]
