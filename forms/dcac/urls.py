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

    path('budgets', views.all_budgets, name='all_budgets'),
    path('budget/<int:budget_id>', views.view_budget, name='view_budget'),
    path('form/budget', views.budget_form, name='budget-form'),
    path('form/budget/submit', views.budget_form_submit, name='budget-submit'),

    path('admin', views.dashboard_admin, name='dashboard-admin'),
    path('admin/requests', views.all_requests_admin, name='all-requests-admin'),
    path('admin/request/<int:form_id>', views.view_request_admin, name='view-request-admin'),
    path('admin/budgets', views.all_budgets_admin, name='all-budgets-admin'),
    path('admin/budgets/<int:year>', views.all_budgets_admin, name='all-budgets-admin-prev-year'),
    path('admin/budget/<int:budget_id>', views.view_budget_admin, name='view-budget-admin'),
    path('admin/profile', views.profile_admin, name='profile-admin'),
]