from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from . import serializers


@api_view(["GET"])
def proj_root(request, format=None):
    return Response({
        "User Registration": reverse(
            "register", request=request, format=format),
        "Quickstart API": reverse(
            "quickstart:api-root", request=request, format=format),
        "Snippets API": reverse(
            "snippets:api-root", request=request, format=format),
    })


class Register(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserCreateSerializer
