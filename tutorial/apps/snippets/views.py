from django.contrib.auth.models import User
from rest_framework import generics

from . import models, serializers

# Create your views here.


class SnippetList(generics.ListCreateAPIView):
    """
    List all code snippets, or create a new snippet.
    """
    queryset = models.Snippet.objects.all()
    serializer_class = serializers.SnippetSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a code snippet.
    """
    queryset = models.Snippet.objects.all()
    serializer_class = serializers.SnippetSerializer


class UserList(generics.ListAPIView):
    """
    List all users.
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class UserDetail(generics.RetrieveAPIView):
    """
    Retrieve a user.
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
