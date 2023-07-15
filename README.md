# studies_django_drf_tutorial

Django Rest Framework (DRF) tutorials

Quickstart: https://www.django-rest-framework.org/tutorial/quickstart/  
Snippets: https://www.django-rest-framework.org/tutorial/1-serialization/

## Concepts

For Django configuration, project installation and other prerequisite knowledge, refer to https://github.com/jobsonita/studies_django_w3tutorial

### Django Rest Framework (DRF)

#### Serializers

[Serializers](https://www.django-rest-framework.org/api-guide/serializers/) do the job of presenting our models in the right way to our renderers and validating received data so that it matches our models. It can restrict which fields are shown, and also add more rules to be checked before accepting the received data.

```python
# models.py
from django.db import models

class Mymodel(models.Model):
    title = models.CharField(max_length=100, blank=False)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

# serializers.py
from rest_framework import serializers
from . import models

class MymodelSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, allow_blank=False, max_length=100)
    content = serializers.CharField(style={'base_template': 'textarea.html'})

    def create(self, validated_data):
        """
        Create and return a new `Mymodel` instance, given the validated data.
        """
        return models.Mymodel.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Mymodel` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance
```

## Common problems

### DRF generates localhost hyperlinks instead of Codespace ones

When using DRF's DefaultRouter to generate [HATEOAS](https://en.wikipedia.org/wiki/HATEOAS) REST links (navigable API), DRF generates localhost hyperlinks. In order to make it generate urls that match the Codespace url, we need to set the `USE_X_FORWARDED_HOST` flag to `True` in the project's `settings.py`. Also, since it will be considered a forwarded request, we need to configure `ALLOWED_HOSTS` to include the Codespace domain, or make it accept any domain by using the `"*"` wildcard.

```python
# settings.py

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

if DEBUG:
    ALLOWED_HOSTS = ["*"]
    USE_X_FORWARDED_HOST = True
else:
    # When in production, configure ALLOWED_HOSTS to accept requests forwarded from the domain where your website is hosted
    ALLOWED_HOSTS = []
```
