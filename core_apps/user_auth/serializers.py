from django.contrib.auth import get_user_model
from djoser.serializers import (UserCreateSerializer as DjoserUserCreateSerializer,)

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