# Standard library imports
import uuid

# Django imports
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Local imports
from .emails import send_account_locked_email
from .managers import UserManager

class User(AbstractUser):
    """
    Custom User model for the school management system.
    Extends Django's AbstractUser to add school-specific functionality.
    
    This model handles user authentication, role management, and security features
    including OTP verification and account locking mechanisms.
    """
    
    class SecurityQuestions(models.TextChoices):
        """
        Predefined security questions for account recovery.
        Used when users need to reset their password or verify identity.
        """
        MAIDEN_NAME = "MAIDEN_NAME", _("What is your mother's maiden name?")
        FAVOURITE_COLOR = "FAVOURITE_COLOR", _("What is your favourite color?")
        BIRTH_CITY = "BIRTH_CITY", _("What is the city where you were born?")
        FAVOURITE_BOOK = "FAVOURITE_BOOK", _("What is your favourite book?")

    class AccountStatus(models.TextChoices):
        """
        Defines the possible states of a user account.
        
        ACTIVE: Normal functioning account with full access
        LOCKED: Account temporarily disabled due to security concerns (e.g., multiple failed login attempts)
        """
        ACTIVE = "ACTIVE", _("Active")
        LOCKED = "LOCKED", _("Locked")

    class RoleChoices(models.TextChoices):
        """
        Defines the available user roles in the school system.
        Each role has different permissions and access levels:
        
        ADMINISTRATOR: Full system access and management capabilities
        TEACHER: Access to class management, grades, and student information
        PARENT: Access to their children's information and performance
        STUDENT: Access to their own academic information and resources
        """
        ADMINISTRATOR = "ADMINISTRATOR", _("Administrator")
        TEACHER = "TEACHER", _("Teacher")
        PARENT = "PARENT", _("Parent")
        STUDENT = "STUDENT", _("Student")

    # Primary key and identification fields
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the user")
    )
    username = models.CharField(
        _("username"),
        max_length=35,
        unique=True,
        help_text=_("Required. 35 characters or fewer for school ID")
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        db_index=True,
        help_text=_("Primary contact email, used for login and communications")
    )
    id_no = models.PositiveIntegerField(
        _("ID number"),
        unique=True,
        help_text=_("Official school identification number")
    )

    # Personal information fields
    first_name = models.CharField(
        _("first name"),
        max_length=30,
        help_text=_("User's first name")
    )
    middle_name = models.CharField(
        _("middle name"),
        max_length=30,
        blank=True,
        null=True,
        help_text=_("User's middle name (optional)")
    )
    last_name = models.CharField(
        _("last name"),
        max_length=30,
        help_text=_("User's last name")
    )

    # Security and account recovery fields
    security_question = models.CharField(
        _("security question"),
        max_length=50,
        choices=SecurityQuestions.choices,
        help_text=_("Question used for account recovery")
    )
    security_answer = models.CharField(
        _("security answer"),
        max_length=50,
        help_text=_("Answer to the security question")
    )
    
    # Account status and role fields
    account_status = models.CharField(
        _("account status"),
        max_length=10,
        choices=AccountStatus.choices,
        default=AccountStatus.ACTIVE,
        help_text=_("Current status of the user account")
    )
    role = models.CharField(
        _("role"),
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.STUDENT,
        help_text=_("User's role in the school system")
    )
    
    # Login security fields
    failed_login_attempts = models.PositiveSmallIntegerField(
        _("failed login attempts"),
        default=0,
        help_text=_("Number of consecutive failed login attempts")
    )
    last_failed_login = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp of the last failed login attempt")
    )
    
    # OTP authentication fields
    otp = models.CharField(
        _("one-time password"),
        max_length=6,
        null=True,
        blank=True,
        help_text=_("Temporary code for two-factor authentication")
    )
    otp_expiry_time = models.DateTimeField(
        _("OTP expiry time"),
        null=True,
        blank=True,
        help_text=_("Timestamp when the current OTP expires")
    )

    # Model configuration
    objects = UserManager()
    USERNAME_FIELD = "email"  # Use email as the primary login identifier
    REQUIRED_FIELDS = ["first_name", "last_name", "id_no", "security_question", "security_answer"]
    
    def set_otp(self, otp: str) -> None:
        """
        Sets a new One-Time Password (OTP) for the user with an expiry time.
        
        Args:
            otp (str): The 6-digit OTP code to be set
            
        The OTP expiry time is calculated by adding settings.OTP_EXPIRY_TIME
        to the current timestamp. After setting, the user instance is saved.
        """
        self.otp = otp
        self.otp_expiry_time = timezone.now() + settings.OTP_EXPIRY_TIME
        self.save()

    def verify_otp(self, otp: str) -> bool:
        """
        Verifies if the provided OTP matches and hasn't expired.
        
        Args:
            otp (str): The OTP code to verify
            
        Returns:
            bool: True if OTP matches and is still valid, False otherwise
            
        Side effects:
            - On successful verification, clears the OTP and its expiry time
            - Saves the user instance after clearing OTP data
        """
        if self.otp == otp and self.otp_expiry_time > timezone.now():
            self.otp = ""
            self.otp_expiry_time = None
            self.save()
            return True
        return False

    def handle_failed_login_attempts(self) -> None:
        """
        Manages the failed login attempts counter and account locking.
        
        Increments the failed login attempts counter and updates the last failed
        login timestamp. If the number of attempts exceeds the maximum allowed,
        locks the account and sends a notification email.
        
        Side effects:
            - Increments failed_login_attempts
            - Updates last_failed_login timestamp
            - May change account_status to LOCKED
            - Sends email notification if account is locked
        """
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        if self.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
            self.account_status = self.AccountStatus.LOCKED
            self.save()
            send_account_locked_email(self)
        self.save()

    def reset_failed_login_attempts(self) -> None:
        """
        Resets all failed login attempt tracking data.
        
        Clears the failed login counter and timestamp, and sets the account
        status back to ACTIVE. Called after a successful login or manual reset.
        """
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.account_status = self.AccountStatus.ACTIVE
        self.save()

    def unlock_account(self) -> None:
        """
        Unlocks a locked account by resetting security tracking fields.
        
        Only processes if the account is currently locked. Resets failed login
        attempts, clears the last failed login timestamp, and sets status to ACTIVE.
        """
        if self.account_status == self.AccountStatus.LOCKED:
            self.account_status = self.AccountStatus.ACTIVE
            self.failed_login_attempts = 0
            self.last_failed_login = None
            self.save()

    @property
    def is_locked_out(self) -> bool:
        """
        Checks if the account is currently locked out.
        
        Returns:
            bool: True if account is locked and lockout period hasn't expired,
                 False otherwise
                 
        Side effects:
            - May unlock the account if the lockout duration has expired
        """
        if self.account_status == self.AccountStatus.LOCKED:
            if(self.last_failed_login and (timezone.now() - self.last_failed_login) > settings.LOCKOUT_DURATION):
                self.unlock_account()
                return False
            return True
        return False

    @property
    def full_name(self) -> str:
        """
        Generates the user's full name including middle name if available.
        
        Returns:
            str: Properly formatted full name with title case
        """
        full_name = f"{self.first_name} {self.last_name}"
        if self.middle_name:
            full_name = f"{self.first_name} {self.middle_name} {self.last_name}"
        return full_name.title().strip()

    def has_role(self, role_name: str) -> bool:
        """
        Checks if the user has a specific role.
        
        Args:
            role_name (str): The role to check against
            
        Returns:
            bool: True if user has the specified role, False otherwise
        """
        return hasattr(self, "role") and self.role == role_name

    def __str__(self) -> str:
        """
        String representation of the user.
        
        Returns:
            str: User's full name and their role display name
        """
        return f"{self.full_name} - {self.get_role_display()}"

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]