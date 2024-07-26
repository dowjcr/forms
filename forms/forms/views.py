import json
from django.db.models.query_utils import Q

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core import serializers
from django.core.exceptions import PermissionDenied
from datetime import datetime

from django.views.generic import TemplateView
from django.views.generic.base import ContextMixin, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView

from .models import *
from dcac.models import ACGReimbursementForm
from budget.models import Budget

from .constants import *
from dcac.constants import *
from .utils import *
from django.conf import settings
import logging

# Mixins

class FormsStudentMixin(LoginRequiredMixin, ContextMixin):
    """Mixin for all student views - student property and authentication"""
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = self.student
        return context

    @property
    def student(self):
        try:
            return Student.objects.get(user_id=self.request.user.username)
        except Student.DoesNotExist:
            raise PermissionDenied("""You could not be found in the student database. This might be because you are a member of the MCR,
            or that the list of students has not been updated for this academic year.""")


class FormsAdminMixin(LoginRequiredMixin, ContextMixin):
    """Mixin for all admin views - user property and authentication"""
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.user
        return context

    @property
    def user(self):
        try:
            return AdminUser.objects.get(user_id=self.request.user.username)
        except AdminUser.DoesNotExist:
            raise PermissionDenied


class LandingView(TemplateView):
    """Shown to user if they are not already authenticated using Raven."""
    template_name = 'forms/landing.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    

class DashboardView(ListView, FormsStudentMixin):
    """Shows summary of requests and clubs for which this user is an owner/administrator"""
    template_name = 'forms/dashboard-student.html'
    context_object_name = 'requests'

    def get_queryset(self):
        return ACGReimbursementForm.objects.filter(submitter=self.student.user_id).order_by('-form_id')[:3]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allow_budget_submit'] = settings.ALLOW_BUDGET_SUBMIT
        context['year'] = settings.CURRENT_YEAR

        return context
    

# --- ADMIN VIEWS ---

class DashboardAdminView(ListView, FormsAdminMixin):
    """Show dashboard with items for user to action."""
    template_name = 'forms/dashboard-admin.html'
    context_object_name = 'requests'

    def get_queryset(self):
        return ACGReimbursementForm.admin_to_action(role=self.user.role)
    

class ProfileAdminView(TemplateView, FormsAdminMixin):
    template_name = 'forms/profile-admin.html'