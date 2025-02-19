from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from core_apps.common.models import TimestampedModel

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
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name

class ClassYear(TimestampedModel):
    year = models.CharField(max_length=100, unique=True, help_text="Example 2020")
    full_name = models.CharField(
        max_length=255, help_text="Example Class_of_2020", blank=True
    )

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = f"Class of {self.year}"
        super().save(*args, **kwargs)

class ReasonLeft(TimestampedModel):
    reason = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.reason

class ClassRoom(TimestampedModel):
    name = models.ForeignKey(
        ClassLevel, on_delete=models.CASCADE, blank=True, related_name="class_level"
    )
    class_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, blank=True)
    capacity = models.PositiveIntegerField(default=40, blank=True)
    occupied_sits = models.PositiveIntegerField(default=0, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "stream"], name="unique_classroom")
        ]

    def __str__(self):
        return f"{self.name} {self.stream}" if self.stream else str(self.name)

    @property
    def available_sits(self):
        return self.capacity - self.occupied_sits

    @property
    def class_status(self):
        percentage = (self.occupied_sits / self.capacity) * 100
        return f"{percentage:.2f}%"

    def clean(self):
        if self.occupied_sits > self.capacity:
            raise ValidationError("Occupied sits cannot exceed the capacity.")

    def save(self, *args, **kwargs):

        self.clean()
        super().save(*args, **kwargs)