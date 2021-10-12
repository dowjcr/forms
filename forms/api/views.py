import json

from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.core import serializers

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, ModelFormMixin

from django.conf import settings
import logging

from forms.models import *
from budget.models import Budget
from dcac.models import ACGReimbursementForm
from forms.views import FormsStudentMixin, FormsAdminMixin

class JSONResponseMixin:
    """Mixin used to return a JSON response"""
    # TODO: add authentication
    def render_to_json_response(self, context, fields=None, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context, fields),
            **response_kwargs
        )

    def get_data(self, context, fields):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        data = serializers.serialize('json', context['object_list'], fields=fields)
        return data


class AllRequestsAPI(ListView, JSONResponseMixin):
    context_object_name = 'requests'
    
    def get_queryset(self):
        return ACGReimbursementForm.objects.order_by('-form_id')

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, safe=False, **response_kwargs)

