"""
URL configuration for quickstart app.
"""
from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register("users", views.UserViewSet)
router.register("groups", views.GroupViewSet)

app_name = "quickstart"
urlpatterns = [
    path("", include(router.urls)),
]
