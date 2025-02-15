import phonenumbers
from typing import Any

from cloudinary.models import CloudinaryField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
#from phonenumber_field.modelfields import PhoneNumberField
from autoslug import AutoSlugField
from django.utils import timezone

from core_apps.common.models import TimestampedModel
from core_apps.academics.models import Subject

User = get_user_model()

def validate_phone_number(value):
        try:
            phone_number = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(phone_number):
                raise ValidationError('Invalid phone number')
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValidationError('Invalid phone number format')

class Profile(TimestampedModel):
    """
    Extended profile information for users in the school system.
    Inherits from TimestampedModel to include creation and update timestamps.
    
    This model stores comprehensive personal and demographic information about users,
    including their identification, contact details, and employment information.
    Photos are stored using Cloudinary for efficient cloud storage and delivery.
    """
    class AccountStatus(models.TextChoices):
        """Enumeration of possible account statuses"""
        ACTIVE = "active", _("Active")
        INACTIVE = "inactive", _("Inactive")

    class Salutation(models.TextChoices):
        """Enumeration of possible salutation titles"""
        MR = ("mr", _("Mr"),)
        MRS = ("mrs", _("Mrs"),)
        MISS = ("miss", _("Miss"),)
        NONE = ("none", _("None"),)

    class Gender(models.TextChoices):
        """Available gender options"""
        MALE = ("male", _("Male"),)
        FEMALE = ("female", _("Female"),)
        OTHER = ("other", _("Other"),)

    class WorkExperience(models.TextChoices):
        """Available work experience options"""
        EXPERINCED = ("experienced", _("Experienced"),)
        FRESHER = ("fresher", _("Fresher"),)
        OTHER = ("other", _("Other"),)

    class MaritalStatus(models.TextChoices):
        """Available marital status options"""
        SINGLE = ("single", _("Single"),)
        MARRIED = ("married", _("Married"),)
        DIVORCED = ("divorced", _("Divorced"),)
        WIDOWED = ("widowed", _("Widowed"),)
        UNKNOWN = ("unknown", _("Unknown"),)

    class IdentificationMeans(models.TextChoices):
        """Types of identification documents accepted"""
        NATIONAL_ID = ("national_id", _("National ID"),)
        PASSPORT = ("passport", _("Passport"),)
        DRIVERS_LICENSE = ("drivers_license", _("Drivers License"),)
        VOTERS_CARD = ("voters_card", _("Voters Card"),)
        NATIONAL_HEALTH_INSURANCE_CARD = ("national_health_insurance_card", _("National Health Insurance Card"),)

    # User Reference
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Personal Information
    title = models.CharField(_("Salutation"), choices=Salutation.choices, max_length=8, default=Salutation.NONE)
    gender = models.CharField(_("Gender"), choices=Gender.choices, max_length=8, default=Gender.MALE)
    date_of_birth = models.DateField(_("Date of Birth"), default=settings.DEFAULT_BIRTH_DATE)
    country_of_birth = CountryField(_("Country of Birth"), default=settings.DEFAULT_COUNTRY)
    place_of_birth = models.CharField(_("Place of Birth"), max_length=55, default="Unknown")
    marital_status = models.CharField(_("Marital Status"), choices=MaritalStatus.choices, max_length=20, default=MaritalStatus.UNKNOWN)

    # Employment Information
    designation = models.CharField(_("Designation"),max_length=255, blank=True, null=True)
    # User's salary
    salary = models.IntegerField(_("Salary"), blank=True, null=True)
    unpaid_salary = models.DecimalField(_("Unpaid Salary"), max_digits=10, decimal_places=2, default=0)
    # Subjects taught by the user
    subjects = models.ManyToManyField(Subject, blank=True)

    # Identification Information
    means_of_identification = models.CharField(
        _("Means of Identification"), 
        choices=IdentificationMeans.choices, 
        max_length=35, 
        default=IdentificationMeans.NATIONAL_ID
    )
    identification_number = models.CharField(_("Identification Number"), max_length=20, blank=True, null=True)
    nationality = models.CharField(_("Nationality"), max_length=35, default="Unknown")

    # Contact Information
    email = models.EmailField(_("Email"), blank=True, null=True)
    phone_number = models.CharField(_("Phone Number"), validators=[validate_phone_number], default=settings.DEFAULT_PHONE_NUMBER, null=True)
    address = models.CharField(_("Address"), max_length=255, blank=True, null=True)
    city = models.CharField(_("City"), max_length=55, default="Unknown", blank=True, null=True)
    state = models.CharField(_("State"), max_length=55, default="Unknown", blank=True, null=True)
    country = CountryField(_("Country"), blank=True, null=True)
    postal_code = models.CharField(_("Postal Code"), max_length=10, blank=True, null=True)

    # Work Experience Information
    experience_status = models.CharField(_("Work Experience"), choices=WorkExperience.choices, max_length=20, default=WorkExperience.OTHER)
    previous_employer = models.CharField(_("Name"), max_length=55, blank=True, null=True)
    years_of_experience = models.CharField(_("Years of Experience"), max_length=20, blank=True, null=True)

    # Profile Media
    photo = CloudinaryField(_("Photo"), blank=True, null=True)
    photo_url = models.URLField(_("Photo URL"), blank=True, null=True)
    id_photo = CloudinaryField(_("ID Photo"), blank=True, null=True)
    id_photo_url = models.URLField(_("ID Photo URL"), blank=True, null=True)
    
    # Future feature: Digital Signature
    # signature_photo = CloudinaryField(_("Signature Photo"), blank=True, null=True)
    # signature_photo_url = models.URLField(_("Signature Photo URL"), blank=True, null=True)

    # Represents the current status of the teacher's account
    # Choices are defined in AccountStatus enum, with INACTIVE as the default state
    account_status = models.CharField(
        _("Account Status"),
        max_length=10,
        choices=AccountStatus.choices,
        default=AccountStatus.INACTIVE,
    )

    # Foreign key to the User who verified this teacher's profile
    # Allows tracking which admin or staff member performed the verification
    # Can be null if no verification has occurred
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="verified_teachers",
        blank=True,
        null=True,
    )

    # Timestamp recording when the teacher's profile was verified
    # Helps in tracking the timeline of account verification
    verification_date = models.DateTimeField(
        _("Verification Date"), blank=True, null=True
    )

    # Optional field to store additional notes or comments during the verification process
    verification_notes = models.TextField(_("Verification Notes"), blank=True)

    # Boolean flag indicating whether the teacher's account is fully activated
    # Provides an additional layer of account status beyond the account_status field
    fully_activated = models.BooleanField(
        _("Fully Activated"), default=False,
    )

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        unique_together = ["user", "subjects", "designation"]

    def __str__(self):
        """String representation of the teacher"""
        return f"{self.title} {self.user.first_name}'s Profile"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Override save method for any future custom save logic"""
        super().save(*args, **kwargs)

    def clean(self):
        """Validate model fields"""
        if self.salary < 0:
            raise ValidationError("Salary cannot be negative")
        
    @property
    def deleted(self):
        # Property to check if the teacher is inactive
        return self.inactive

    # Custom method to update unpaid salary at the start of each month
    def update_unpaid_salary(self):
        # Update unpaid salary at the start of each month
        current_month = timezone.now().month
        if self.unpaid_salary > 0:
            self.unpaid_salary += self.salary  # Add salary amount to unpaid salary
        else:
            self.unpaid_salary = (
                self.salary
            )  # If unpaid salary is 0, set the first month's salary
        self.save()
    
    
