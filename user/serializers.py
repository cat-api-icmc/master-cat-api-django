from rest_framework import serializers
from user.models import User


class SimpleUserSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="uuid", read_only=True)

    class Meta:
        model = User
        fields = ("id", "name", "username", "email")
