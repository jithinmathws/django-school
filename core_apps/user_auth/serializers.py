from django.contrib.auth import get_user_model
from djoser.serializers import (UserCreateSerializer as DjoserUserCreateSerializer, UserSerializer as DjoserUserSerializer)
from rest_framework import serializers

User = get_user_model()

class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = [
            "email",
            "username",
            "password",
            "id_no",
            "first_name",
            "middle_name",
            "last_name",
            "security_question",
            "security_answer",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class CustomUserSerializer(DjoserUserSerializer):
    full_name = serializers.ReadOnlyField(source="user.full_name")
    slug = serializers.ReadOnlyField(source="user.slug")
    email = serializers.EmailField(source="user.email", read_only=True)
    role = serializers.ReadOnlyField(source="user.role")

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "middle_name",
            "last_name",
            "full_name",
            "slug",
            "email",
            "role",
        ]
    
        read_only_fields = ["id", "username", "email"]
