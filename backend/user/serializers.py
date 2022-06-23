from accounts.models import (
    Administrator, Student, User
)
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db import transaction
from django.utils.encoding import (
    DjangoUnicodeDecodeError, force_str,
    smart_bytes, smart_str
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import update_last_login
from django.core.exceptions import ObjectDoesNotExist


class UserSerializer(CountryFieldMixin,
                     serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "full_name",
                  "email", "phone", "role", "is_active",
                  "timestamp")
        read_only_field = ("id", "email", "timestamp")


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['user'] = UserSerializer(self.user).data
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)
        return data
    
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, max_length=128
    )

    class Meta:
        model = User
        fields = [
            "username", "email", "phone", "full_name",
            "role",
        ]

    def create(self, validated_data):
        try:
            user = User.objects.get(email=validated_data["email"])
        except ObjectDoesNotExist:
            user = User.objects.create(
                username=validated_data["username"],
                email=validated_data["email"],
                phone=validated_data["phone"],
                is_active=False,
                full_name=validated_data["full_name"],
                role=validated_data['role']
            )
            user.save()
        return user
    
class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=155, min_length=2
    )

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        return attrs


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True, required=True
    )
    password_confirmation = serializers.CharField(
        min_length=6, max_length=68, write_only=True, required=True
    )
    token = serializers.CharField(min_length=1, write_only=True, required=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True
    )

    class Meta:
        fields = ('password', 'password_confirmation', 'token', 'uidb64')

class AdministratorProfileSerializer(CountryFieldMixin, serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Administrator
        fields = ("id", "user", "gender")
        
        read_only_fields = ("id",)
        
class AdministratorProfileSerializer(CountryFieldMixin, serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ("id", "user", "gender")
        
        read_only_fields = ("id",)

