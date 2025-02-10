from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TeacherProfileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_apps.teacher_profile'
    verbose_name = _("Teacher Profile")
