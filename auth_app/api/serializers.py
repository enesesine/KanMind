from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token

from auth_app.models import CustomUser


# ==========================
# 1) Registration Serializer
# ==========================

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Handles user registration. Requires password confirmation.
    """
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("fullname", "email", "password", "repeated_password")

    def validate_email(self, value):
        # Ensure email is unique
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already taken.")
        return value

    def validate(self, attrs):
        # Ensure both password fields match
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError({
                "repeated_password": "Passwords do not match."
            })
        return attrs

    def create(self, validated_data):
        # Remove repeated_password and hash the real password
        validated_data.pop("repeated_password")
        password = validated_data.pop("password")
        email = validated_data["email"]

        user = CustomUser(
            email=email,
            fullname=validated_data.get("fullname", ""),
            username=email,  # username is required internally by Django
        )
        user.set_password(password)
        user.save()
        return user


# ==========================
# 2) Lightweight User Serializer
# ==========================

class UserMiniSerializer(serializers.ModelSerializer):
    """
    Returns minimal user information (id, email, fullname).
    """
    class Meta:
        model  = CustomUser
        fields = ("id", "email", "fullname")


# ==========================
# 3) Email Existence Check Serializer
# ==========================

class EmailCheckSerializer(serializers.Serializer):
    """
    Validates whether an email is already registered.
    """
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs["email"].lower()
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "Email does not exist."}, code="not_found"
            )
        attrs["user"] = user
        return attrs
