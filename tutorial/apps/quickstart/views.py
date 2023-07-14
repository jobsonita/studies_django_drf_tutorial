from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions

from . import serializers as quickstart_serializers


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = quickstart_serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = quickstart_serializers.GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
