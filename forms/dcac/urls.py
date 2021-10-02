"""
URLS
Defines URL paths which match to Django views.
Author Cameron O'Connor
"""

from django.urls import path
from . import views
from .views import *
from django.views.generic.base import RedirectView

# as all urls were initially made from dcac app, old links begin with dcac/
# include urls from previous project structure, so that old links still work

compatibility_urls = [
    path('welcome/', RedirectView.as_view(pattern_name='landing')),
    path('dashboard/', RedirectView.as_view(pattern_name='dashboard')),
    path('admin/', RedirectView.as_view(pattern_name='dashboard-admin')),
    path('admin/profile/', RedirectView.as_view(pattern_name='profile-admin')),
    path('form/acg/', RedirectView.as_view(url='acg-standard'), name='acg'),
    
    path('budgets/', RedirectView.as_view(pattern_name='all-budgets')),
    path('budget/<int:budget_id>/', RedirectView.as_view(pattern_name='view-budget')),
    path('form/budget/', RedirectView.as_view(pattern_name='budget-form')),

    path('admin/budgets/', RedirectView.as_view(pattern_name='all-budgets-admin')),
    path('admin/budgets/<int:year>/', RedirectView.as_view(pattern_name='all-budgets-admin-prev-year')),
    path('admin/budget/<int:budget_id>/', RedirectView.as_view(pattern_name='view-budget-admin')),
]

urlpatterns = [
    path('requests/', AllRequestsView.as_view(), name='all-requests'),
    path('request/<int:form_id>/', DetailRequestView.as_view(), name='view-request'),
    path('form/acg-<str:request_type>/', AcgFormView.as_view(), name='acg-form'),

    path('admin/requests/', AllRequestsAdminView.as_view(), name='all-requests-admin'),
    path('admin/request/<int:form_id>/', DetailRequestAdminView.as_view(), name='view-request-admin'),
] + compatibility_urls