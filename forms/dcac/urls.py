"""
URLS
Defines URL paths which match to Django views.
Author Cameron O'Connor
"""

from django.urls import path
from . import views
from django.views.generic.base import RedirectView


urlpatterns = [
    path('welcome', views.landing, name='landing'),
    path('dashboard', views.dashboard, name='dashboard'),
    
    path('requests', views.all_requests, name='all-requests'),
    path('request/<int:form_id>', views.view_request, name='view-request'),
    path('form/acg', RedirectView.as_view(url='acg-standard'), name='acg'),
    path('form/acg-<str:request_type>', views.acg_form, name='acg-form'),
    path('form/acg/submit', views.acg_form_submit, name='acg-submit'),


    path('admin', views.dashboard_admin, name='dashboard-admin'),
    path('admin/requests', views.all_requests_admin, name='all-requests-admin'),
    path('admin/request/<int:form_id>', views.view_request_admin, name='view-request-admin'),
    path('admin/profile', views.profile_admin, name='profile-admin'),
]