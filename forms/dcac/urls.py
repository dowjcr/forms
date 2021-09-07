"""
URLS
Defines URL paths which match to Django views.
Author Cameron O'Connor
"""

from django.urls import path
from . import views
from django.views.generic.base import RedirectView

# as all urls were initially made from dcac app, old links begin with dcac/
# urls from previous project structure, so that old links still work

compatibility_urls = [
    path('welcome/', RedirectView.as_view(pattern_name='landing-welcome')),
    path('dashboard/', RedirectView.as_view(pattern_name='dashboard')),
    path('admin/', RedirectView.as_view(pattern_name='dashboard-admin')),
    
    path('budgets/', RedirectView.as_view(pattern_name='all-budgets')),
    path('budget/<int:budget_id>/', RedirectView.as_view(pattern_name='view-budget')),
    path('form/budget/', RedirectView.as_view(pattern_name='budget-form')),
    path('form/budget/submit/', RedirectView.as_view(pattern_name='budget-submit')),

    path('admin/budgets/', RedirectView.as_view(pattern_name='all-budgets-admin')),
    path('admin/budgets/<int:year>/', RedirectView.as_view(pattern_name='all-budgets-admin-prev-year')),
    path('admin/budget/<int:budget_id>/', RedirectView.as_view(pattern_name='view-budget-admin')),
]

urlpatterns = [
    path('requests/', views.all_requests, name='all-requests'),
    path('request/<int:form_id>/', views.view_request, name='view-request'),
    path('form/acg/', RedirectView.as_view(url='acg-standard'), name='acg'),
    path('form/acg-<str:request_type>/', views.acg_form, name='acg-form'),
    path('form/acg/submit/', views.acg_form_submit, name='acg-submit'),

    path('admin/requests/', views.all_requests_admin, name='all-requests-admin'),
    path('admin/request/<int:form_id>/', views.view_request_admin, name='view-request-admin'),
    path('admin/profile/', views.profile_admin, name='profile-admin'),
] + compatibility_urls