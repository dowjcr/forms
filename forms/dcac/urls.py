"""
URLS
Defines URL paths which match to Django views.
Author Cameron O'Connor
"""

from django.urls import path
from . import views


urlpatterns = [
    path('welcome', views.landing, name='landing'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('request/<int:form_id>', views.view_request, name='view-request'),
    path('form/acg', views.acg_form, name='acg'),

    path('admin/request/<int:form_id>', views.view_request_admin, name='view-request-admin')
]