from django.contrib import admin
from .models import Department, Subject

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name"]
    list_display_links = ["name"]
    search_fields = ["name"]

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["name", "subject_code", "department"]
    list_display_links = ["name"]
    search_fields = ["name", "subject_code"]
    list_filter = ["department"]
    ordering = ["department", "name"]