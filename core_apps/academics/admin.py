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

@admin.register(ClassName)
class ClassNameAdmin(admin.ModelAdmin):
    list_display = ["name"]
    list_display_links = ["name"]
    search_fields = ["name"]

@admin.register(ClassYear)
class ClassYearAdmin(admin.ModelAdmin):
    list_display = ["year", "full_name"]
    list_display_links = ["year"]
    search_fields = ["year", "full_name"]
    ordering = ["-year"]

@admin.register(ReasonLeft)
class ReasonLeftAdmin(admin.ModelAdmin):
    list_display = ["reason"]
    list_display_links = ["reason"]
    search_fields = ["reason"]

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ["name", "class_teacher", "capacity", "occupied_sits"]
    list_display_links = ["name"]
    search_fields = ["name", "class_teacher"]
    list_filter = ["class_teacher", "name"]
    ordering = ["class_teacher", "name", "capacity"]