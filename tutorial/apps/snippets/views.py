from django.contrib.auth.models import User
from rest_framework import filters, permissions, renderers, reverse, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from . import models
from . import permissions as snippets_permissions
from . import serializers

# Create your views here.


@api_view(["GET"])
def api_root(request, format=None):
    return Response({
        "snippets": reverse.reverse(
            "snippets:snippet-list", request=request, format=format),
        "users": reverse.reverse(
            "snippets:user-list", request=request, format=format),
    })


class SnippetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = models.Snippet.objects.all()
    serializer_class = serializers.SnippetSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        snippets_permissions.IsOwnerOrReadOnly]

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["username"]
    ordering = ["username"]
