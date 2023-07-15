from django.urls import path

from . import views as snippets_views

urlpatterns = [
    path('snippets/', snippets_views.snippet_list),
    path('snippets/<int:pk>/', snippets_views.snippet_detail),
]
