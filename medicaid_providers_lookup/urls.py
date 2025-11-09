from django.urls import path
from . import views

urlpatterns = [
    path('search-providers/', views.search_providers, name='search_providers'),
]