from rest_framework import generics

from . import models, serializers

# Create your views here.


class SnippetList(generics.ListCreateAPIView):
    """
    List all code snippets, or create a new snippet.
    """
    queryset = models.Snippet.objects.all()
    serializer_class = serializers.SnippetSerializer


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a code snippet.
    """
    queryset = models.Snippet.objects.all()
    serializer_class = serializers.SnippetSerializer
