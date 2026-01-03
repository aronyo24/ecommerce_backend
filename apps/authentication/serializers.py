import random
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import OTP, UserProfile
from .utils import generate_otp, send_otp_email

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'profile_picture', 'address', 'role', 'is_email_verified']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        name = validated_data.pop('name')
        email = validated_data['email']
        password = validated_data.pop('password')
        
        username = email.split('@')[0]
        if User.objects.filter(username=username).exists():
            username = f"{username}_{random.randint(100, 999)}"

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=name,
            is_active=False
        )
        
        otp_code = generate_otp()
        OTP.objects.create(user=user, otp_code=otp_code)
        send_otp_email(email, otp_code)
        
        return user

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

