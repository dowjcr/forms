import datetime

from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from django.conf import settings
import logging

from rest_framework.generics import ListAPIView
from rest_framework.permissions import BasePermission

from .serializers import RequestSerializer
from forms.models import *
from budget.models import Budget
from dcac.models import ACGReimbursementForm
    

class FormsAdminUserPermission(BasePermission):
    """Allow requests for logged-in admin users"""
    def has_permission(self, request, view):
        return AdminUser.objects.filter(
            user_id=request.user
        ).exists()


class FormsAPIKeyPermission(BasePermission):
    """Allow requests using an API key"""
    # TODO: Allow user-speicific API keys
    def has_permission(self, request, view):
        return request.GET.get('api_key')  == settings.API_KEY


class AllRequestsAPI(ListAPIView):
    context_object_name = 'requests'
    serializer_class = RequestSerializer
    permission_classes = [FormsAdminUserPermission | FormsAPIKeyPermission]
    
    def get_queryset(self):
        """Return all requests starting from the 1st of September for the current academic year"""
        from_date = datetime.datetime(settings.CURRENT_YEAR, 9, 1)

        return ACGReimbursementForm.objects.filter(
            date__gt=from_date
        ).order_by('-form_id')
   