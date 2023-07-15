from rest_framework import serializers

from . import models as snippets_models


class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = snippets_models.Snippet
        fields = ['id', 'title', 'code', 'linenos', 'language', 'style']
