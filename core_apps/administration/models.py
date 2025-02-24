from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .common_objs import *
from core_apps.common.models import TimestampedModel

User = get_user_model()

class Article(TimestampedModel):
    """Model representing an article with title, content, and associated media."""
    title = models.CharField(_("Title"), max_length=155, blank=True, null=True)
    content = models.TextField(_("Content"), blank=True, null=True)
    picture = CloudinaryField(_("Photo"), blank=True, null=True)
    picture_url = models.URLField(_("Photo URL"), blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    
    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")

class CarouselImage(TimestampedModel):
    title = models.CharField(_("Title"), max_length=155, blank=True, null=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    picture = CloudinaryField(_("Photo"), blank=True, null=True)
    picture_url = models.URLField(_("Photo URL"), blank=True, null=True)
    
    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = _("Carousel Image")
        verbose_name_plural = _("Carousel Images")

class School(TimestampedModel):
    active = models.BooleanField(default=False, help_text="This will be used to activate or deactivate the school")
    name = models.CharField(_("School Name"), max_length=255, help_text="Name of the school")
    address = models.CharField(_("Address"), max_length=255, help_text="Address of the school")
    school_type = models.CharField(
        _("School Type"),
        max_length=50,
        choices=SCHOOL_TYPE_CHOICE, # Choices for different types of schools
        blank=True,
        null=True,
        help_text="Type of school",
    )
    gender_allowed = models.CharField(
        _("Gender Allowed"),
        max_length=50,
        choices=SCHOOL_STUDENTS_GENDER, # Choices for gender of students allowed
        blank=True,
        null=True,
        help_text="Gender of students allowed",
    )
    ownership = models.CharField(
        _("Ownership"),
        max_length=50,
        choices=SCHOOL_OWNERSHIP,  # Choices for ownership of school
        blank=True,
        null=True,
        help_text="Ownership of school",
    )
    mission = models.TextField(_("Mission"), blank=True, null=True, help_text="Mission of the school")
    vision = models.TextField(_("Vision"), blank=True, null=True, help_text="Vision of the school")
    telephone = models.CharField(_("Telephone"), max_length=20, blank=True, null=True, help_text="Telephone number of the school")
    email = models.EmailField(_("Email"), blank=True, null=True, help_text="Email of the school")
    school_logo = CloudinaryField(_("School Logo"), blank=True, null=True)
    school_logo_url = models.URLField(_("School Logo URL"), blank=True, null=True)
    
    def __str__(self) -> str:
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["active"]),
        ]
        ordering = ["name"]
        verbose_name = _("School")
        verbose_name_plural = _("Schools")

class Day(TimestampedModel):
    DAY_CHOICES = (
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
        (7, "Sunday"),
    )
    day = models.IntegerField(
        choices=DAY_CHOICES,
        unique=True,
        help_text="Day of the week",
    )
    
    def __str__(self) -> str:
        return (self.get_day_display())

    class Meta:
        ordering = ["day"]
        verbose_name = _("Day")
        verbose_name_plural = _("Days")

class AcademicYear(TimestampedModel):
    name = models.CharField(_("Name"), max_length=255, unique=True, help_text="Name of the academic year (e.g. 2024-2025)")
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    student_completion = models.DateField(blank=True, null=True, help_text="Date of student completion")
    active_year = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["-start_date"]
        verbose_name = _("Academic Year")
        verbose_name_plural = _("Academic Years")

    @property
    def status(self):
        if self.active_year:
            return _("Active")
        elif self.start_date <= timezone.now() <= self.end_date:
            return _("Ongoing")
        elif self.start_date > timezone.now() > self.end_date:
            return _("Completed")
        return _("Inactive")

    def save(self, *args, **kwargs):
        if self.active_year:
            AcademicYear.objects.exclude(pk=self.pk).update(active_year=False)
        super().save(*args, **kwargs)

    def clean(self):
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError(_("End date must be after start date."))

        super().clean()

class Term(TimestampedModel):
    name = models.CharField(_("Name"), max_length=50, help_text="If in term1, term2, term3, etc.")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="terms")
    default_term_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=15000,
        help_text="Default term fee",
    )
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.academic_year.name})"