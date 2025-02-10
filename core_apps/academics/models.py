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

class Teacher(TimestampedModel):
    # Model representing a teacher
    class AccountStatus(models.TextChoices):
        ACTIVE = "active", _("Active")
        INACTIVE = "inactive", _("Inactive")

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher",
        verbose_name=_("Teacher"),
        null=True,
        blank=True,
    )
    empId = models.UUIDField(verbose_name=_("Object ID"))
    isTeacher = models.BooleanField(default=True)
    salary = models.IntegerField(blank=True, null=True)
    unpaid_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subjects = models.ManyToManyField(Subject, blank=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    account_status = models.CharField(
        _("Account Status"),
        max_length=10,
        choices=AccountStatus.choices,
        default=AccountStatus.INACTIVE,
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="verified_teachers",
        blank=True,
        null=True,
    )
    verification_date = models.DateTimeField(
        _("Verification Date"), blank=True, null=True
    )
    verification_notes = models.TextField(_("Verification Notes"), blank=True)
    fully_activated = models.BooleanField(
        _("Fully Activated"), default=False,
    )

    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"
        unique_together = ["user", "subjects", "designation"]

    def __str__(self) -> str:
        return self.user.get_full_name()

    def clean(self):
        if self.salary < 0:
            raise ValidationError("Salary cannot be negative")
    
    @property
    def deleted(self):
        # Property to check if the teacher is inactive
        return self.inactive
    
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