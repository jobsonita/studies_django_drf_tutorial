from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = "snippets"
urlpatterns = format_suffix_patterns([
    path("snippets/", views.SnippetList.as_view()),
    path("snippets/<int:pk>/", views.SnippetDetail.as_view()),
])
