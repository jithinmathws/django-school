from django.contrib import admin
from cloudinary.forms import CloudinaryFileField
from django import forms
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Profile

class ProfileAdminForm(forms.ModelForm):
    """
    Custom form for Profile model in admin interface.
    Extends ModelForm to handle Cloudinary image upload with specific configuration.
    """
    photo = CloudinaryFileField(
        options={"crop": "thumb", "width": 200, "height": 200, "folder": "school_photo"},
        required=False,
    )

    class Meta:
        model = Profile
        fields = "__all__"

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Profile model.
    Customizes the display, filtering, and organization of profile information in the admin interface.
    """
    form = ProfileAdminForm  # Use custom form for Cloudinary image handling
    
    # Configure which fields appear in the list view
    list_display = [
        "user",
        "full_name",
        "email",
        "phone_number",
        "photo_preview",
    ]
    list_display_links = ["user"]  # Make user field clickable for detail view
    
    # Add filtering options in the right sidebar
    list_filter = [
        "gender",
        "country",
    ]
    
    # Configure search functionality
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "phone_number",
    ]
    
    readonly_fields = ["user"]  # Prevent user field from being modified
    
    # Organize fields into logical groups using fieldsets
    fieldsets = (
        (
            _("Personal Information"),
            {
                "fields": (
                    "user",
                    "photo",
                    "id_photo",
                    "title",
                    "gender",
                    "date_of_birth",
                )
            },
        ),
        (
            _("Contact Information"),
            {
                "fields": (
                    "phone_number",
                    "email",
                    "country",
                    "city",
                    "address",
                )
            },
        ),
        (
            _("Identification Information"),
            {"fields": ("identification_number", "identification_means")},
        ),
    )

    def full_name(self, obj) -> str:
        """
        Returns the full name of the user associated with the profile.
        
        Args:
            obj: Profile instance
            
        Returns:
            str: User's full name
        """
        return obj.user.full_name
    
    full_name.short_description = _("Full Name")

    def email(self, obj) -> str:
        """
        Returns the email of the user associated with the profile.
        
        Args:
            obj: Profile instance
            
        Returns:
            str: User's email
        """
        return obj.user.email
    
    email.short_description = _("Email")

    def photo_preview(self, obj) -> str:
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.photo.url,
            )
        return "No photo"

    photo_preview.short_description = _("Photo")