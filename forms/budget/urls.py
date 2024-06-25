from django.urls import path
from .views import *


urlpatterns = [
    path('budgets/', AllBudgetsView.as_view(), name='all-budgets'),
    path('usage/', BudgetUsageView.as_view(), name="budget-usage-student"),
    path('usage/<int:budget_id>/', SingleBudgetUsageView.as_view(), name="budget-usage-single-student"),
    path('budget/<int:budget_id>/', DetailBudgetView.as_view(), name='view-budget'),
    path('edit/<int:budget_id>/', UpdateBudgetView.as_view(), name='edit-budget'),
    path('form/', CreateBudgetView.as_view(), name='budget-form'),

    path('admin/budgets/', AllBudgetsAdminView.as_view(), name='all-budgets-admin'),
    path('admin/budgets/<int:year>/', AllBudgetsAdminView.as_view(), name='all-budgets-admin-prev-year'),
    path('admin/budget/<int:budget_id>/', DetailBudgetAdminView.as_view(), name='view-budget-admin'),
    path('admin/usage/', BudgetUsageAdminView.as_view(), name="budget-usage-admin"),
    path('admin/usage/<int:budget_id>/', SingleBudgetUsageAdminView.as_view(), name="budget-usage-single-admin"),
]