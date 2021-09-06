import json
from django.db.models.query_utils import Q

from django.shortcuts import redirect, render, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core import serializers
from django.core.exceptions import PermissionDenied
from datetime import datetime

from .models import *
from dcac.models import *
from budget.models import *

from .constants import *
from .utils import *
from django.conf import settings
import logging

# LANDING PAGE
# Shown to user if they are not already authenticated
# using Raven.

def landing(request):
    if not request.user.is_authenticated:
        return render(request, 'forms/landing.html')
    else:
        return redirect('dashboard')


# DASHBOARD
# Shows summary of requests and clubs for which this
# user is an owner/administrator.

@login_required(login_url='/accounts/login/')
def dashboard(request):
    student = user_or_403(request, Student)
    print(settings.BASE_DIR, settings.STATICFILES_DIRS)

    requests = ACGReimbursementForm.objects.filter(submitter=student.user_id).order_by('-form_id')[:3]

    return render(request, 'forms/dashboard-student.html', {
        'requests': requests,
        'student': student,
        'allow_budget_submit': settings.ALLOW_BUDGET_SUBMIT,
        'year': settings.CURRENT_YEAR,
        })


# --- ADMIN VIEWS ---
# ADMIN DASHBOARD
# Show dashboard with items for user to action.

@login_required(login_url='/accounts/login/')
def dashboard_admin(request):
    user = user_or_403(request, AdminUser)

    if user.role == AdminRoles.JCRTREASURER:
        requests = ACGReimbursementForm.objects.filter(
            rejected=False, jcr_treasurer_approved=False
        ).order_by('form_id')
    elif user.role == AdminRoles.SENIORTREASURER:
        requests = ACGReimbursementForm.objects.filter(
            rejected=False, jcr_treasurer_approved=True, senior_treasurer_approved=False
        ).order_by('form_id')
    elif user.role == AdminRoles.BURSARY:
        requests = ACGReimbursementForm.objects.filter(
            jcr_treasurer_approved=True, senior_treasurer_approved=True, bursary_paid=False
        ).order_by('form_id')
    elif user.role == AdminRoles.ASSISTANTBURSAR:
        requests = ACGReimbursementForm.objects.filter(
            jcr_treasurer_approved=True, senior_treasurer_approved=True, bursary_paid=False
        ).filter(reimbursement_type=RequestTypes.LARGE).order_by('form_id')
    else:
        requests = []
    return render(request, 'forms/dashboard-admin.html', {
        'user': user,
        'requests': requests
        })