# Generated by Django 5.1.5 on 2025-01-26 10:26

import core_apps.user_profile.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_profile", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="phone_number",
            field=models.CharField(
                default="+91 0000000000",
                null=True,
                validators=[core_apps.user_profile.models.validate_phone_number],
                verbose_name="Phone Number",
            ),
        ),
    ]
