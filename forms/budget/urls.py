from django.urls import path
from . import views
from django.views.generic.base import RedirectView


urlpatterns = [
    path('budgets', views.all_budgets, name='all-budgets'),
    path('budget/<int:budget_id>', views.view_budget, name='view-budget'),
    path('form/budget', views.budget_form, name='budget-form'),
    path('form/budget/submit', views.budget_form_submit, name='budget-submit'),

    path('admin/budgets', views.all_budgets_admin, name='all-budgets-admin'),
    path('admin/budgets/<int:year>', views.all_budgets_admin, name='all-budgets-admin-prev-year'),
    path('admin/budget/<int:budget_id>', views.view_budget_admin, name='view-budget-admin'),
]