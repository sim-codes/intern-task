from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _

# Create your models here.

class CustomUserManager(UserManager):
    """
    Custom user manager for User model.
    
    Provides methods to create regular users and superusers with email and full_name fields.
    """
    
    def _create_user(self, email, full_name, password, **extra_fields):
        """
        Create and save a user with the given email, full name, and password.
        
        Args:
            email: User's email address
            full_name: User's full name
            password: User's password
            **extra_fields: Additional fields for user creation
            
        Returns:
            User: Created user instance
            
        Raises:
            ValueError: If email or full_name is not provided
        """
        if not email:
            raise ValueError('The Email field must be set')
        if not full_name:
            raise ValueError('The Full Name field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, full_name, password=None, **extra_fields):
        """
        Create a regular user.
        
        Args:
            email: User's email address
            full_name: User's full name
            password: User's password (optional)
            **extra_fields: Additional fields
            
        Returns:
            User: Created user instance
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, full_name, password, **extra_fields)

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        """
        Create a superuser.
        
        Args:
            email: Superuser's email address
            full_name: Superuser's full name
            password: Superuser's password
            **extra_fields: Additional fields
            
        Returns:
            User: Created superuser instance
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, full_name, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    
    Uses email as the username field and requires full_name.
    Removes the default username field in favor of email-based authentication.
    """
    username = None  # Remove username field
    full_name = models.CharField(max_length=150, verbose_name=_('Full Name'), help_text=_('User\'s full name'))
    email = models.EmailField(_('email address'), unique=True, help_text=_('User\'s email address (unique identifier)'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()

    def __str__(self):
        """Return string representation of the user (email)."""
        return self.email
