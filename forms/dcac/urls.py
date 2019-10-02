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
    path('requests', views.all_requests, name='all-requests'),
    path('request/<int:form_id>', views.view_request, name='view-request'),
    path('form/acg', views.acg_form, name='acg'),
    path('form/acg/submit', views.acg_form_submit, name='acg-submit'),

    path('admin/request/<int:form_id>', views.view_request_admin, name='view-request-admin'),
    path('admin/profile', views.profile_admin, name='profile-admin')
]