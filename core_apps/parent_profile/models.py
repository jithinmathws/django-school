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

    class RelationshipChoice(models.TextChoices):
        """Available relationship options"""
        FATHER = ("father", _("Father"),)
        MOTHER = ("mother", _("Mother"),)
        GUARDIAN = ("guardian", _("Guardian"),)

    class IdentificationMeans(models.TextChoices):
        """Types of identification documents accepted"""
        NATIONAL_ID = ("national_id", _("National ID"),)
        PASSPORT = ("passport", _("Passport"),)
        DRIVERS_LICENSE = ("drivers_license", _("Drivers License"),)
        VOTERS_CARD = ("voters_card", _("Voters Card"),)
        NATIONAL_HEALTH_INSURANCE_CARD = ("national_health_insurance_card", _("National Health Insurance Card"),)

    class EmploymentStatus(models.TextChoices):
        """Available employment status options"""
        EMPLOYED = ("employed", _("Employed"),)
        UNEMPLOYED = ("unemployed", _("Unemployed"),)
        SELF_EMPLOYED = ("self_employed", _("Self-Employed"),)
        RETIRED = ("retired", _("Retired"),)
        STUDENT = ("student", _("Student"),)
        HOUSEWIFE = ("housewife", _("Housewife"),)
        OTHER = ("other", _("Other"),)

    '''class OtherRoles(models.TextChoices):
        """Available other roles for users"""
        ACCOUNTANT = ("accountant", _("Accountant"),)
        STUDENT = ("student", _("Student"),)'''

    # User Reference
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Personal Information
    title = models.CharField(_("Salutation"), choices=Salutation.choices, max_length=8, default=Salutation.NONE)
    gender = models.CharField(_("Gender"), choices=Gender.choices, max_length=8, default=Gender.MALE)
    parent_type = models.CharField(_("Parent Type"), choices=RelationshipChoice.choices, max_length=8, default=RelationshipChoice.GUARDIAN)
    single_parent = models.BooleanField(default=False, blank=True, help_text="Is he/she a single parent")
    date_of_birth = models.DateField(_("Date of Birth"), default=settings.DEFAULT_BIRTH_DATE)
    country_of_birth = CountryField(_("Country of Birth"), default=settings.DEFAULT_COUNTRY)
    place_of_birth = models.CharField(_("Place of Birth"), max_length=55, default="Unknown")

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

    # Employment Information
    employment_status = models.CharField(_("Employment Status"), choices=EmploymentStatus.choices, max_length=20, default=EmploymentStatus.OTHER)

    # Profile Media
    photo = CloudinaryField(_("Photo"), blank=True, null=True)
    photo_url = models.URLField(_("Photo URL"), blank=True, null=True)
    id_photo = CloudinaryField(_("ID Photo"), blank=True, null=True)
    id_photo_url = models.URLField(_("ID Photo URL"), blank=True, null=True)
    
    # Future feature: Digital Signature
    # signature_photo = CloudinaryField(_("Signature Photo"), blank=True, null=True)
    # signature_photo_url = models.URLField(_("Signature Photo URL"), blank=True, null=True)

    is_active = models.BooleanField(_("Is Active"), default=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Override save method for any future custom save logic"""
        super().save(*args, **kwargs)

    def clean(self):
        """Validate model fields"""
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError({'date_of_birth': _('Date of birth cannot be in the future')})
        
        super().clean()

    def __str__(self):
        """String representation of the profile"""
        return f"{self.title} {self.user.first_name}'s Profile"

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        unique_together = ["user", "parent_type"]
