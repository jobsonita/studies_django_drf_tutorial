from django.contrib.auth.models import User
from rest_framework import serializers

from . import models


class SnippetSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = models.Snippet
        fields = [
            "id", "title", "code", "linenos", "language", "style", "owner"]


class UserSerializer(serializers.ModelSerializer):
    snippets = serializers.PrimaryKeyRelatedField(
        many=True, queryset=models.Snippet.objects.all())

    class Meta:
        model = User
        fields = ["id", "username", "snippets"]
