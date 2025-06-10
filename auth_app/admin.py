from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from auth_app.models import CustomUser

from rest_framework.authtoken.models import Token


# ==========================
# Custom User Model Admin
# ==========================

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin panel configuration for the custom user model."""
    model = CustomUser

    list_display  = ("email", "fullname", "is_staff", "is_active")
    list_filter   = ("is_staff", "is_active")
    ordering      = ("email",)
    search_fields = ("email", "fullname")

    # Fields shown when editing an existing user
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("fullname",)}),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important Dates", {"fields": ("last_login",)}),
    )

    # Fields shown when creating a new user via admin
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "fullname",
                "password1",
                "password2",
                "is_staff",
                "is_active",
            ),
        }),
    )


# ==========================
# Token Model Admin
# ==========================

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    """Admin panel configuration for auth tokens."""
    list_display  = ("key", "user", "created")
    search_fields = ("key", "user__email")
    ordering      = ("-created",)
