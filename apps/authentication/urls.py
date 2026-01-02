from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterViewSet,
    VerifyOTPViewSet,
    LoginViewSet,
    ForgotPasswordViewSet,
    PasswordResetVerifyViewSet,
    ResendOTPViewSet,
    UserProfileView
)

router = DefaultRouter()
router.register('register', RegisterViewSet, basename='register')
router.register('verify-otp', VerifyOTPViewSet, basename='verify-otp')
router.register('login', LoginViewSet, basename='login')
router.register('forgot-password', ForgotPasswordViewSet, basename='forgot-password')
router.register('reset-password', PasswordResetVerifyViewSet, basename='reset-password')
router.register('resend-otp', ResendOTPViewSet, basename='resend-otp')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserProfileView.as_view(), name='profile'),
]
