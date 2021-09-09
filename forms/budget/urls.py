from django.urls import path
from .views import *


urlpatterns = [
    path('budgets/', AllBudgetsView.as_view(), name='all-budgets'),
    path('budget/<int:budget_id>/', DetailBudgetView.as_view(), name='view-budget'),
    path('edit/<int:budget_id>/', UpdateBudgetView.as_view(), name='edit-budget'),
    path('form/', CreateBudgetView.as_view(), name='budget-form'),

    path('admin/budgets/', AllBudgetsAdminView.as_view(), name='all-budgets-admin'),
    path('admin/budgets/<int:year>/', AllBudgetsAdminView.as_view(), name='all-budgets-admin-prev-year'),
    path('admin/budget/<int:budget_id>/', DetailBudgetAdminView.as_view(), name='view-budget-admin'),
]