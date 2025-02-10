from django.contrib import admin
from .models import Department, Subject, Teacher

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

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ["user", "empId", "subjects", "designation"]
    list_display_links = ["user", "subjects"]
    search_fields = ["user", "subjects"]
    list_filter = ["designation", "subjects"]
    ordering = ["subjects", "user", "empId"]