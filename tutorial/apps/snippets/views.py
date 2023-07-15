from django.contrib.auth.models import User
from rest_framework import generics, permissions, renderers, reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import models
from . import permissions as snippets_permissions
from . import serializers

# Create your views here.


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'snippets': reverse.reverse(
            'snippets:snippet-list', request=request, format=format),
        'users': reverse.reverse(
            'snippets:user-list', request=request, format=format),
    })


class SnippetList(generics.ListCreateAPIView):
    """
    List all code snippets, or create a new snippet.
    """
    queryset = models.Snippet.objects.all()
    serializer_class = serializers.SnippetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a code snippet.
    """
    queryset = models.Snippet.objects.all()
    serializer_class = serializers.SnippetSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        snippets_permissions.IsOwnerOrReadOnly]


class SnippetHighlight(generics.GenericAPIView):
    """
    Retrieve the highlighted version of a code snippet.
    """
    queryset = models.Snippet.objects.all()
    renderer_classes = [renderers.StaticHTMLRenderer]

    def get(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)


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
