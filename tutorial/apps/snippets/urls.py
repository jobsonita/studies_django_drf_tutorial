"""
URL configuration for snippets app.
"""
from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register("snippets", views.SnippetViewSet)
router.register("users", views.UserViewSet)

app_name = "snippets"
urlpatterns = [
    path("", include(router.urls)),
]
