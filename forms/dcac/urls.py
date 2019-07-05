"""
URLS
Defines URL paths which match to Django views.
Author Cameron O'Connor
"""

from django.urls import path
from . import views


urlpatterns = [
    path('welcome', views.landing, name='landing')
]