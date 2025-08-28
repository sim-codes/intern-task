from rest_framework import generics, permissions, status, generics
from .models import User
from .serializers import UserRegistrationSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import random
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .throttling import LoginThrottle, PasswordResetThrottle, PasswordResetConfirmThrottle, RegistrationThrottle


@extend_schema(
    summary="Register a new user",
    description="Create a new user account with email, full name, and password.",
    request=UserRegistrationSerializer,
    responses={
        201: UserRegistrationSerializer,
        400: OpenApiTypes.OBJECT,
        429: {
            'type': 'object',
            'properties': {
                'detail': {'type': 'string', 'description': 'Rate limit exceeded'},
            }
        },
    },
    tags=['Authentication']
)
class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    
    Allows new users to create an account by providing their full name, email, and password.
    The email must be unique across all users.
    Rate limited to 10 registrations per hour per IP address.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    throttle_classes = [RegistrationThrottle]


@extend_schema(
    summary="User login",
    description="Authenticate user and return JWT access and refresh tokens.",
    request={
        'type': 'object',
        'properties': {
            'email': {'type': 'string', 'format': 'email'},
            'password': {'type': 'string', 'format': 'password'},
        },
        'required': ['email', 'password']
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'access': {'type': 'string', 'description': 'JWT access token'},
                'refresh': {'type': 'string', 'description': 'JWT refresh token'},
            }
        },
        401: OpenApiTypes.OBJECT,
        429: {
            'type': 'object',
            'properties': {
                'detail': {'type': 'string', 'description': 'Rate limit exceeded'},
            }
        },
    },
    tags=['Authentication']
)
class UserLoginView(TokenObtainPairView):
    """
    API endpoint for user login.
    
    Authenticates user credentials and returns JWT tokens for API access.
    Rate limited to 5 attempts per minute per IP address.
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginThrottle]


from .serializers import ForgotPasswordSerializer, ResetPasswordSerializer


@extend_schema(
    summary="Request password reset",
    description="Send a password reset token to the user's email address.",
    request=ForgotPasswordSerializer,
    responses={
        200: {
            'type': 'object',
            'properties': {
                'reset_token': {'type': 'string', 'description': 'Password reset token (for development)'},
            }
        },
        404: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string', 'description': 'User not found message'},
            }
        },
        429: {
            'type': 'object',
            'properties': {
                'detail': {'type': 'string', 'description': 'Rate limit exceeded'},
            }
        },
    },
    tags=['Password Management']
)
class ForgotPasswordView(generics.GenericAPIView):
    """
    API endpoint for requesting password reset.
    
    Generates a reset token and stores it in cache for 10 minutes.
    In production, this would send the token via email.
    Rate limited to 3 requests per hour per IP address.
    """
    serializer_class = ForgotPasswordSerializer
    throttle_classes = [PasswordResetThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        token = str(random.randint(100000, 999999))
        cache.set(f'pwd-reset-{token}', user.pk, timeout=600)
        # In production, token would be sent via email
        return Response({'reset_token': token}, status=status.HTTP_200_OK)


@extend_schema(
    summary="Reset password",
    description="Reset user password using the reset token.",
    request=ResetPasswordSerializer,
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string', 'description': 'Success message'},
            }
        },
        400: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string', 'description': 'Invalid or expired token message'},
            }
        },
        429: {
            'type': 'object',
            'properties': {
                'detail': {'type': 'string', 'description': 'Rate limit exceeded'},
            }
        },
    },
    tags=['Password Management']
)
class ResetPasswordView(generics.GenericAPIView):
    """
    API endpoint for resetting password.
    
    Validates the reset token and updates the user's password.
    The token expires after 10 minutes.
    Rate limited to 10 attempts per hour per IP address.
    """
    serializer_class = ResetPasswordSerializer
    throttle_classes = [PasswordResetConfirmThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        user_id = cache.get(f'pwd-reset-{token}')
        if not user_id:
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(pk=user_id)
        user.password = make_password(new_password)
        user.save()
        cache.delete(f'pwd-reset-{token}')
        return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)
