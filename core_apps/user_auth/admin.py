from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User
from .forms import UserChangeForm, UserCreationForm

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin configuration for the User model.
    
    Extends Django's UserAdmin to provide a customized admin interface for managing users.
    """
    form = UserChangeForm
    add_form = UserCreationForm
    model = User

    # Fields to display in the user list view
    list_display = [
        'email',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'role',
    ]

    # Fields available for filtering in the right sidebar
    list_filter = ['email', 'is_staff', 'is_active', 'role']

    # Configuration for the user detail view, organized in sections
    fieldsets = (
        (
            _("Login Credentials"),  # Authentication information
            {
                "fields": (
                    "username",
                    "email",
                    "password",
                )
            },
        ),
        (
            _("Personal Information"),  # User's personal details
            {
                "fields": (
                    "first_name",
                    "middle_name",
                    "last_name",
                    "id_no",
                    "role"
                )
            },
        ),
        (
            _("Account Status"),  # Account security and status tracking
            {
                "fields": (
                    "account_status",
                    "failed_login_attempts",
                    "last_failed_login",
                )
            },
        ),
        (
            _("Security Questions"),  # Account recovery information
            {
                "fields": (
                    "security_question",
                    "security_answer",
                )
            },
        ),
        (
            _("Permissions and Groups"),  # User permissions configuration
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Important Dates"),  # Automatically tracked timestamps
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    # Fields available for searching users
    search_fields = ['email', 'username', 'first_name', 'last_name']
    
    # Default ordering in the admin list view
    ordering = ["email"]
