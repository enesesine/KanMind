from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from auth_app.models import CustomUser

from rest_framework.authtoken.models import Token



# CustomUser im Admin

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display  = ("email", "fullname", "is_staff", "is_active")
    list_filter   = ("is_staff", "is_active")
    ordering      = ("email",)
    search_fields = ("email", "fullname")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Persönliche Daten", {"fields": ("fullname",)}),
        (
            "Berechtigungen",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Wichtiges", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "fullname",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )



# Token-Liste im Admin & übersichtlicher

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display  = ("key", "user", "created")
    search_fields = ("key", "user__email")
    ordering      = ("-created",)
