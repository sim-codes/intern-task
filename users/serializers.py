from rest_framework import serializers
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Handles creation of new user accounts with validation for required fields.
    """
    password = serializers.CharField(write_only=True, help_text="User's password (write-only)")
    
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'password']
        read_only_fields = ['id']
        extra_kwargs = {
            'full_name': {'help_text': 'User\'s full name'},
            'email': {'help_text': 'User\'s email address (must be unique)'},
        }

    def create(self, validated_data):
        """
        Create a new user instance.
        
        Args:
            validated_data: Validated serializer data
            
        Returns:
            User: Newly created user instance
        """
        user = User(
            email=validated_data['email'],
            full_name=validated_data['full_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    
    Validates email address for password reset functionality.
    """
    email = serializers.EmailField(help_text="Email address of the user requesting password reset")


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    
    Validates reset token and new password for password reset.
    """
    token = serializers.CharField(help_text="Password reset token received via email")
    new_password = serializers.CharField(help_text="New password for the user account")


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    
    Validates email and password for user authentication.
    """
    email = serializers.EmailField(help_text="User's email address")
    password = serializers.CharField(help_text="User's password", write_only=True)
