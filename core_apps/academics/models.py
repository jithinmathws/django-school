from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from shortuuid.django_fields import ShortUUIDField

from core_apps.common.models import TimestampedModel
from administration.models import *
from administration.common_objs import *

User = get_user_model()

class Department(TimestampedModel):
    # Model representing a department
    name = models.CharField(_("Department Name"), max_length=255, unique=True)

    def __str__(self):
        return self.name

class Subject(TimestampedModel):
    # Model representing a subject
    name = models.CharField(_("Subject Name"), max_length=255, unique=True)
    subject_code = models.CharField(_("Subject code"), max_length=10, blank=True, null=True, unique=True)
    is_selective = models.BooleanField(
        default=False, help_text="Select if this subject is optional"
    )
    is_graded = models.BooleanField(default=True, help_text="Teachers can grade students")
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    def save(self, *args, **kwargs):
        # Override save method to modify name and description before saving
        self.name = self.name.upper()
        self.description = f"{self.name.lower()} - {self.subject_code}"
        super().save(*args, **kwargs)

class ClassName(TimestampedModel):
    name = models.CharField(_("Class Name"), max_length=150, unique=True)

    def __str__(self):
        return self.name

class ClassYear(TimestampedModel):
    year = models.CharField(_("Class Year"),max_length=100, unique=True, help_text="Example 2020")
    full_name = models.CharField(_("Full Name"), max_length=255, help_text="Example Class_of_2020", blank=True, null=True)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = f"Class of {self.year}"
        super().save(*args, **kwargs)

class ReasonLeft(TimestampedModel):
    reason = models.CharField(_("Reason for Leaving"), max_length=255, unique=True)

    def __str__(self):
        return self.reason

class ClassRoom(TimestampedModel):
    name = models.ForeignKey(
        ClassName, on_delete=models.CASCADE, blank=True, related_name="class_name"
    )
    class_teacher = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    capacity = models.PositiveIntegerField(_("Capacity"), default=40, blank=True)
    occupied_seats = models.PositiveIntegerField(_("Occupied Seats"), default=0, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "stream"], name="unique_classroom")
        ]

    def __str__(self):
        return f"{self.name}"

    @property
    def available_sits(self):
        return self.capacity - self.occupied_seats

    @property
    def class_status(self):
        percentage = (self.occupied_seats / self.capacity) * 100
        return f"{percentage:.2f}%"

    def clean(self):
        if self.occupied_seats > self.capacity:
            raise ValidationError("Occupied seats cannot exceed the capacity.")


    def save(self, *args, **kwargs):

        self.clean()
        super().save(*args, **kwargs)

class Topic(TimestampedModel):
    name = models.CharField(_("Topic Name"), max_length=255, blank=True, null=True)
    class_name = models.ForeignKey(ClassName, on_delete=models.CASCADE, blank=True, related_name="class_name")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=True, related_name="subject")

    def __str__(self):
        return f"{self.name}"

class SubTopic(TimestampedModel):
    name = models.CharField(_("Sub Topic Name"), max_length=255, blank=True, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, blank=True, related_name="topic")

    def __str__(self):
        return f"{self.name}"

class AllocatedSubject(TimestampedModel):
    teacher_name = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name="teacher_name")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=True, related_name="subject")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, blank=True, related_name="academic_year")
    term = models.OneToOneField(Term, on_delete=models.CASCADE, blank=True, related_name="term")
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, blank=True, related_name="class_room")
    period_per_week = models.PositiveIntegerField(_("Period Per Week"), blank=True, help_text="Subject will be allocated to the classroom based on the period per week.")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["teacher_name", "subject", "academic_year", "term", "class_room"], name="unique_allocated_subject")
        ]

    def __str__(self):
        return f"{self.teacher_name} - {self.subject} - {self.academic_year} - {self.class_room}"
    
    def subjects_data(self):
        return list(self.subject.all())

class Student(TimestampedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("Active")
        INACTIVE = "INACTIVE", _("Inactive")
        SUSPENDED = "SUSPENDED", _("Suspended")
        GRADUATED = "GRADUATED", _("Graduated")
        TRANSFERRED = "TRANSFERRED", _("Transferred")
        DROPPED = "DROPPED", _("Dropped")
        WITHDRAWN = "WITHDRAWN", _("Withdrawn")
        DECEASED = "DECEASED", _("Deceased")
        OTHER = "OTHER", _("Other")
    
    class Gender_Choice(models.TextChoices):
        MALE = "MALE", _("Male")
        FEMALE = "FEMALE", _("Female")
        OTHER = "OTHER", _("Other")
    
    first_name = models.CharField(_("First Name"), max_length=255, blank=True, null=True)
    last_name = models.CharField(_("Last Name"), max_length=255, blank=True, null=True)
    middle_name = models.CharField(_("Middle Name"), max_length=255, blank=True, null=True)
    gender = models.CharField(_("Gender"), choices=Gender_Choice.choices, max_length=8, default=Gender_Choice.MALE)
    date_of_birth = models.DateField(_("Date of Birth"), default=settings.DEFAULT_BIRTH_DATE)
    country_of_birth = CountryField(_("Country of Birth"), default=settings.DEFAULT_COUNTRY)
    place_of_birth = models.CharField(_("Place of Birth"), max_length=55, default="Unknown")
    graduation_date = models.DateField(_("Graduation Date"), blank=True, null=True)
    class_name = models.ForeignKey(ClassName, on_delete=models.SET_NULL, blank=True, related_name="class_name")
    class_year = models.ForeignKey(ClassYear, on_delete=models.SET_NULL, blank=True, related_name="class_year")
    date_dismissed = models.DateField(_("Date Dismissed"), blank=True, null=True)
    reason_left = models.ForeignKey(ReasonLeft, on_delete=models.SET_NULL, blank=True, null=True)
    religion = models.CharField(_("Religion"), max_length=255, blank=True, null=True)
    residence_region = models.CharField(_("Residence Region"), max_length=255, blank=True, null=True)
    city = models.CharField(_("City"), max_length=255, blank=True, null=True)
    blood_group = models.CharField(_("Blood Group"), max_length=255, blank=True, null=True)
    parent = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name="parent")
    guardian = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name="guardian")
    admission_number = ShortUUIDField(length=6, max_length=10, alphabet="1234567890")
