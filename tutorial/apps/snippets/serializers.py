from rest_framework import serializers

from . import models


class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Snippet
        fields = ["id", "title", "code", "linenos", "language", "style"]
