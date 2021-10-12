from django.urls import path
from .views import *


urlpatterns = [
    # path('budgets/', AllBudgetsAPI.as_view(), name='all-budgets'),
    path('requests/', AllRequestsAPI.as_view(), name='all-requests-api'),
]