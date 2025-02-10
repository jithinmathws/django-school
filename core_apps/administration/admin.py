from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author',]
    list_display_links = ['title',]
    search_fields = ['title', 'author',]

@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ['title',]
    list_display_links = ['title',]
    search_fields = ['title',]

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'school_type', 'ownership', 'telephone', 'email',]
    list_display_links = ['name', 'school_type',]
    search_fields = ['name', 'school_type', 'ownership', 'telephone', 'email',]
    list_filter = ['school_type', 'ownership',]

@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ['day',]
    list_display_links = ['day',]
    search_fields = ['day',]

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date',]
    list_display_links = ['name',]
    search_fields = ['name',]

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['name', 'academic_year',]
    list_display_links = ['name', 'academic_year',]
    search_fields = ['name', 'academic_year',]