from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from auth_app.models import CustomUser
from auth_app.api.serializers import RegistrationSerializer


# ==========================
# Registration View
# ==========================
class RegistrationView(APIView):
    """
    Registers a new user.
    POST /api/registration/
    Expected body:
    {
      "fullname": "Max Mustermann",
      "email":    "max@test.com",
      "password": "superSecret123!",
      "repeated_password": "superSecret123!"
    }
    Returns user info and token on success.
    """
    permission_classes: list = []  # Public endpoint

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token":    token.key,
                "user_id":  user.id,
                "fullname": user.fullname,
                "email":    user.email,
            },
            status=status.HTTP_201_CREATED,
        )


# ==========================
# Login View
# ==========================
class LoginView(APIView):
    """
    Authenticates a user.
    POST /api/login/
    Expected body:
    {
      "email":    "max@test.com",
      "password": "superSecret123!"
    }
    Returns token and user info on success.
    """
    permission_classes: list = []  # Public endpoint

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"detail": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        users_qs = CustomUser.objects.filter(email=email)
        if not users_qs.exists():
            return Response({"detail": "Invalid credentials."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = users_qs.first()

        if not user.check_password(password):
            return Response({"detail": "Invalid credentials."},
                            status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token":    token.key,
                "user_id":  user.id,
                "fullname": user.fullname,
                "email":    user.email,
            },
            status=status.HTTP_200_OK,
        )


# ==========================
# Email Check View
# ==========================
class EmailCheckView(APIView):
    """
    Checks if a given email exists.
    GET /api/email-check/?email=<addr>
    Requires authentication.

    * 200: user info found
    * 404: email not found
    * 400: parameter missing or invalid format
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response({"detail": "email parameter missing."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError:
            return Response({"detail": "invalid email format."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            return Response(
                {"id": user.id, "email": user.email, "fullname": user.fullname},
                status=status.HTTP_200_OK,
            )
        except CustomUser.DoesNotExist:
            return Response({"detail": "email not found."},
                            status=status.HTTP_404_NOT_FOUND)
