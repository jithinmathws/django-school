"""
Custom user manager for handling user creation and authentication in the school management system.
This module provides functionality for creating regular users and superusers with email-based authentication.
"""

from random import choices
import string
from os import getenv
from typing import Any, Optional

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _


def generate_username() -> str:
    """
    Generate a unique username based on school name and random characters.
    
    Format: [SCHOOL_INITIALS]--[RANDOM_CHARS]
    Example: If school name is "Outshine School", username might be "OS--A1B2C3D4E5"
    
    Returns:
        str: A unique username string of maximum length 15 characters
    """
    school_name = getenv("SCHOOL_NAME")
    words = school_name.split()
    # Get initials from school name
    prefix = "".join([word[0] for word in words]).upper()
    # Calculate remaining length for random characters
    remaining_length = 12 - len(prefix) - 1
    # Generate random alphanumeric string
    random_chars = "".join(choices(string.ascii_uppercase + string.digits, k=remaining_length))
    username = f"{prefix}--{random_chars}"
    return username


def validate_email_address(email: str) -> None:
    """
    Validate email address using Django's built-in validator.
    
    Args:
        email (str): Email address to validate
        
    Raises:
        ValidationError: If email address is invalid
    """
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError(
            _("Please enter a valid email address"),
            code="invalid_email_address",
        )


class UserManager(DjangoUserManager):
    """
    Custom user manager for handling user operations with email-based authentication.
    Extends Django's default UserManager with custom user creation logic.
    """
    
    def _create_user(self, email: str, password: str, **extra_fields: Any):
        """
        Base method for creating users with email authentication.
        
        Args:
            email (str): User's email address
            password (str): User's password
            **extra_fields: Additional fields for user model
            
        Returns:
            User: Created user instance
            
        Raises:
            ValueError: If email or password is not provided
        """
        if not email:
            raise ValueError(_("The given email must be provided"))
        
        if not password:
            raise ValueError(_("A password must be provided"))

        # Generate unique username and validate email
        username = generate_username()
        email = self.normalize_email(email)
        validate_email_address(email)

        # Create and save user instance
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: Optional[str] = None, **extra_fields: Any):
        """
        Create and save a regular user with the given email and password.
        
        Args:
            email (str): User's email address
            password (Optional[str]): User's password
            **extra_fields: Additional fields for user model
            
        Returns:
            User: Created regular user instance
        """
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: Optional[str] = None, **extra_fields: Any):
        """
        Create and save a superuser with the given email and password.
        
        Args:
            email (str): Superuser's email address
            password (Optional[str]): Superuser's password
            **extra_fields: Additional fields for user model
            
        Returns:
            User: Created superuser instance
            
        Raises:
            ValueError: If is_staff or is_superuser is not True
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
            
        return self._create_user(email, password, **extra_fields)