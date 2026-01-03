from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTP
from .utils import generate_otp, send_otp_email
from .serializers import (
    UserRegistrationSerializer, 
    VerifyOTPSerializer, 
    ForgotPasswordSerializer, 
    PasswordResetSerializer,
    UserSerializer,
    LoginSerializer
)

class RegisterViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "OTP sent to your email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            try:
                user = User.objects.get(email=email)
                otp_obj = OTP.objects.get(user=user, otp_code=otp_code)
                user.is_active = True
                user.save()
                
                # Update profile verification status
                if hasattr(user, 'profile'):
                    user.profile.is_email_verified = True
                    user.profile.save()
                    
                otp_obj.delete()
                return Response({"message": "Account activated successfully."}, status=status.HTTP_200_OK)
            except (User.DoesNotExist, OTP.DoesNotExist):
                return Response({"error": "Invalid OTP or Email."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(username=user_obj.username, password=password)
            if user:
                if not user.is_active:
                    return Response({"error": "Account not verified. Please verify OTP."}, status=status.HTTP_403_FORBIDDEN)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                })
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class ForgotPasswordViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                otp_code = generate_otp()
                OTP.objects.update_or_create(user=user, defaults={'otp_code': otp_code})
                send_otp_email(email, otp_code, subject="Password Reset OTP")
                return Response({"message": "Reset OTP sent to your email."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User with this email not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetVerifyViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            new_password = serializer.validated_data['new_password']
            try:
                user = User.objects.get(email=email)
                otp_obj = OTP.objects.get(user=user, otp_code=otp_code)
                user.set_password(new_password)
                user.save()
                
                # Also ensure verified if they reset password successfully
                if hasattr(user, 'profile'):
                    user.profile.is_email_verified = True
                    user.profile.save()
                    
                otp_obj.delete()
                return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
            except (User.DoesNotExist, OTP.DoesNotExist):
                return Response({"error": "Invalid OTP or Email."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response({"message": "Account already active."}, status=status.HTTP_400_BAD_REQUEST)
            otp_code = generate_otp()
            OTP.objects.update_or_create(user=user, defaults={'otp_code': otp_code})
            send_otp_email(email, otp_code)
            return Response({"message": "New OTP sent to your email."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
