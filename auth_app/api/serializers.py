
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token

from auth_app.models import CustomUser



# 1) Serializer für die Registrierung

from rest_framework import serializers
from auth_app.models import CustomUser

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("fullname", "email", "password", "repeated_password")

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Diese E-Mail ist bereits vergeben.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError({"repeated_password": "Passwörter stimmen nicht überein."})
        return attrs

    def create(self, validated_data):
      
        validated_data.pop("repeated_password")
        password = validated_data.pop("password")

     
        email = validated_data["email"]
        user = CustomUser(
            email=email,
            fullname=validated_data.get("fullname", ""),
            username=email,           
        )
        user.set_password(password)
        user.save()
        return user



# 2) Mini-Darstellung eines Users (z. B. in Board-Antworten)

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CustomUser
        fields = ("id", "email", "fullname")



# 3) E-Mail-Check 

class EmailCheckSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs["email"].lower()
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "E-Mail existiert nicht."}, code="not_found"
            )
        attrs["user"] = user
        return attrs
