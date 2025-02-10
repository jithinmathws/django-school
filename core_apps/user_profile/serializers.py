import base64
from typing import Any, Dict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django_countries.serializers_fields import CountryField
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from core_apps.common.models import ContentView
from .models import Profile
from .tasks import upload_profile_picture

User = get_user_model()

class UUIDField(serializers.Field):
    def to_representation(self, value: str) -> str:
        return str(value)

class ProfileSerializer(serializers.ModelSerializer):
    id = UUIDField(read_only=True)
    first_name = serializers.CharField(source="user.first_name")
    middle_name = serializers.CharField(source="user.middle_name", required=False, allow_blank=True)
    last_name = serializers.CharField(source="user.last_name")
    username = serializers.ReadOnlyField(source="user.username")
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.ReadOnlyField(source="user.full_name")
    id_no = serializers.ReadOnlyField(source="user.id_no")
    date_joined = serializers.DateTimeField(source="user.date_joined", read_only=True)
    country_of_birth = CountryField(name_only=True)
    country = CountryField(name_only=True)
    phone_number = PhoneNumberField()
    photo = serializers.ImageField(write_only=True, required=False)
    id_photo = serializers.ImageField(write_only=True, required=False)

    photo_url = serializers.URLField(read_only=True)
    id_photo_url = serializers.URLField(read_only=True)
    view_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id",
            "first_name",
            "middle_name",
            "last_name",
            "username",
            "slug",
            "email",
            "full_name",
            "id_no",
            "date_joined",
            "country_of_birth",
            "address",
            "city",
            "country",
            "phone_number",
            "photo",
            "id_photo",
            "photo_url",
            "id_photo_url",
            "created_at",
            "updated_at",
            "view_count",
        ]
        read_only_fields = [
            "id",
            "username",
            "slug",
            "email",
            "created_at",
            "updated_at",
            "view_count",
        ]

    def to_representation(self, instance: Profile) -> dict:
        representation = super().to_representation(instance)
        return representation

    def update(self, instance: Profile, validated_data: dict) -> Profile:
        user_data = validated_data.pop("user", {})
        if user_data:
            for attr, value in user_data.items():
                if attr not in ["email", "username"]:
                    setattr(instance.user, attr, value)
            instance.user.save()

        photos_to_upload = {}

        for field in ["photo", "id_photo"]:
            if field in validated_data:
                photos_to_upload[field] = validated_data.pop(field)
                if photo.size > settings.MAX_UPLOAD_SIZE:
                    temp_file = default_storage.save(
                        f"temp_{instance.id}_{field}.jpg", ContentFile(photo.read())
                    )
                    temp_file_path = default_storage.path(temp_file)
                    photos_to_upload[field] = {"type": "file", "path": temp_file_path}
                else:
                    image_content = photo.read()
                    encoded_image = base64.b64encode(image_content).decode("utf-8")
                    photos_to_upload[field] = {"type": "base64", "data": encoded_image}

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if photos_to_upload:
            upload_photos_to_cloudinary.delay(str(instance.id), photos_to_upload)

        return instance
    
    def get_view_count(self, obj: Profile) -> int:
        content_type = ContentType.objects.get_for_model(obj)
        return ContentView.objects.filter(content_type=content_type, object_id=obj.id).count()

class ProfileListSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source="user.full_name")
    username = serializers.ReadOnlyField(source="user.username")
    email = serializers.EmailField(source="user.email", read_only=True)
    photo = serializers.ImageField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "full_name",
            "username",
            "gender",
            "nationality",
            "country_of_birth",
            "email",
            "phone_number",
            "photo"
        ]

    def get_photo(self, obj: Profile) -> str:
        try:
            return obj.photo.url
        except AttributeError:
            return None