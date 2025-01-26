from django.contrib import admin
from typing import Any
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.admin import GenericInlineModelAdmin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import ContentView

@admin.register(ContentView)
class ContentViewAdmin(admin.ModelAdmin):
    """
    Admin configuration for ContentView model.
    Provides a read-only interface to view and analyze content viewing patterns.
    """
    # Display these fields as columns in the list view
    list_display = ['content_object', 'content_type', 'user', 'viewer_ip', 'last_viewed']
    
    # Enable filtering by these fields in the right sidebar
    list_filter = ['content_type', 'last_viewed', 'created_at']
    
    # Enable date-based navigation
    date_hierarchy = 'last_viewed'
    
    # Make all fields read-only since views should only be created programmatically
    readonly_fields = ['content_type', 'object_id', 'content_object', 'user', 'viewer_ip', 'created_at', 'updated_at']
    
    # Organize fields into logical sections
    fieldsets = (
        (None, {
            'fields': ('content_type', 'object_id', 'content_object')
        }),
        (_("View Details"), {
            'fields': ('user', 'viewer_ip', 'last_viewed')
        }),
        (_("Timestamps"), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Disable manual creation of views through admin interface"""
        return False
    
    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        """Disable editing of views through admin interface"""
        return False

class ContentViewInline(GenericTabularInline):
    """
    Inline admin configuration for ContentView model.
    Can be included in other models' admin to show their associated views.
    All fields are read-only as views should only be created programmatically.
    """
    model = ContentView
    extra = 0  # Don't show any empty forms
    readonly_fields = ['user', 'viewer_ip', 'created_at', 'last_viewed']
    can_delete = False  # Prevent deletion through inline

    def has_add_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        """Disable manual creation of views through inline admin"""
        return False