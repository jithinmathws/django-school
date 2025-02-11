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