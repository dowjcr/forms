import json

from django.shortcuts import render, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from datetime import datetime
from simplecrypt import encrypt, decrypt
from .models import *
from .email import *
from django.conf import settings
import logging

LOG_FILE = 'dcac.log'
ENCRYPTION_KEY = settings.ENCRYPTION_KEY
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


# LANDING PAGE
# Shown to user if they are not already authenticated
# using Raven.

def landing(request):
    if not request.user.is_authenticated:
        return render(request, 'dcac/landing.html')
    else:
        return HttpResponseRedirect('/dcac/dashboard')


# DASHBOARD
# Shows summary of requests and clubs for which this
# user is an owner/administrator.

@login_required(login_url='/accounts/login/')
def dashboard(request):
    student = Student.objects.get(user_id=request.user.username)

    requests = ACGReimbursementForm.objects.filter(submitter=student.user_id).order_by('-form_id')[:3]

    return render(request, 'dcac/dashboard-student.html', {'requests': requests,
                                                           'student': student})


# ALL REQUESTS
# Allow student to view all requests they have made.

@login_required(login_url='/accounts/login/')
def all_requests(request):
    student = Student.objects.get(user_id=request.user.username)
    requests = ACGReimbursementForm.objects.filter(submitter=student.user_id).order_by('-form_id')
    return render(request, 'dcac/all-requests-student.html', {'student': student,
                                                              'requests': requests})


# VIEW REQUEST
# For student to view details of previous request.

@login_required(login_url='/accounts/login/')
def view_request(request, form_id):
    student = Student.objects.get(user_id=request.user.username)
    acg_request = get_object_or_404(ACGReimbursementForm, pk=form_id)
    items = ACGReimbursementFormItemEntry.objects.filter(form_id=acg_request)
    return render(request, 'dcac/view-request-student.html', {'student': student,
                                                              'request': acg_request,
                                                              'items': items})


# ACG FORM
# Allows student to fill out ACG reimbursement form.

@login_required(login_url='/accounts/login/')
def acg_form(request):
    student = Student.objects.get(user_id=request.user.username)
    if request.method == 'POST':
        file_entry = ACGReimbursementFormReceiptEntry()
        file_entry.file = request.FILES['receipt']
        file_entry.save()
        return HttpResponse(json.dumps({'receipt_id': file_entry.entry_id}), content_type="application/json")
    else:
        return render(request, 'dcac/acg-form-student.html', {'student': student,
                                                              'organizations': Organization.objects.order_by('name')})


# ACG FORM SUBMIT
# Allows submission of completed form.

@login_required(login_url='/accounts/login/')
def acg_form_submit(request):
    student = Student.objects.get(user_id=request.user.username)
    if request.method == 'POST':
        organization = Organization.objects.get(organization_id=request.POST.get('organization'))
        items = json.loads(request.POST.get('items'))
        receipts = json.loads(request.POST.get('receipts'))
        sort_code = request.POST.get('sort_code')
        account_number = request.POST.get('account_number')
        name_on_account = request.POST.get('name_on_account')
        total = 0

        form = ACGReimbursementForm()
        form.organization = organization
        form.date = datetime.now()
        form.sort_code = encrypt(ENCRYPTION_KEY, sort_code)
        form.account_number = encrypt(ENCRYPTION_KEY, account_number)
        form.name_on_account = name_on_account
        form.submitter = student.user_id

        form.save()

        for item in items:
            total += float(item['amount'])
            entry = ACGReimbursementFormItemEntry()
            entry.form = form
            entry.title = item['title']
            entry.description = item['description']
            entry.amount = item['amount']
            entry.save()

        for receipt in receipts:
            entry = ACGReimbursementFormReceiptEntry.objects.get(entry_id=receipt)
            entry.form = form
            entry.save()

        form.amount = total
        form.save()

        notify_junior_treasurer(form)

        return HttpResponse(json.dumps({'formId': form.form_id}), content_type="application/json")


# ADMIN DASHBOARD
# Show dashboard with items for user to action.

@login_required(login_url='/accounts/login/')
def dashboard_admin(request):
    user = AdminUser.objects.get(user_id=request.user.username)
    if user.role == 1:      # Junior Treasurer
        requests = ACGReimbursementForm.objects.filter(rejected=False, jcr_treasurer_approved=False).order_by('form_id')
    elif user.role == 2:    # Senior Treasurer
        requests = ACGReimbursementForm.objects.filter(rejected=False, jcr_treasurer_approved=True, senior_treasurer_approved=False).order_by('form_id')
    elif user.role == 3:    # Bursary
        requests = ACGReimbursementForm.objects.filter(jcr_treasurer_approved=True, senior_treasurer_approved=True).order_by('form_id')
    else:
        requests = []
    return render(request, 'dcac/dashboard-admin.html', {'user': user,
                                                         'requests': requests})


# ADMIN VIEW REQUEST
# For admin to view details of request.

@login_required(login_url='/accounts/login/')
def view_request_admin(request, form_id):
    user = AdminUser.objects.get(user_id=request.user.username)
    acg_request = get_object_or_404(ACGReimbursementForm, pk=form_id)
    if request.method == 'POST':
        # Clicked 'approve'.
        comments = request.POST.get('comments')
        if request.POST.get('code') == '1':
            if user.role == 1:
                acg_request.jcr_treasurer_approved = True
                acg_request.jcr_treasurer_comments = comments
                acg_request.jcr_treasurer_date = datetime.now()
                acg_request.jcr_treasurer_name = str(user)
                notify_senior_treasurer(acg_request)
            elif user.role == 2:
                acg_request.senior_treasurer_approved = True
                acg_request.senior_treasurer_comments = comments
                acg_request.senior_treasurer_date = datetime.now()
                acg_request.senior_treasurer_name = str(user)
            acg_request.save()
        elif request.POST.get('code') == '2':
            acg_request.rejected = True
            if user.role == 1:
                acg_request.jcr_treasurer_approved = False
                acg_request.jcr_treasurer_comments = comments
                acg_request.jcr_treasurer_date = datetime.now()
                acg_request.jcr_treasurer_name = str(user)
            elif user.role == 2:
                acg_request.senior_treasurer_approved = False
                acg_request.senior_treasurer_comments = comments
                acg_request.senior_treasurer_date = datetime.now()
                acg_request.senior_treasurer_name = str(user)
            acg_request.save()

        return HttpResponse(json.dumps({'responseCode': 1}), content_type="application/json")

    items = ACGReimbursementFormItemEntry.objects.filter(form=acg_request)
    receipts = ACGReimbursementFormReceiptEntry.objects.filter(form=acg_request)
    if user.role == 3:
        acg_request.sort_code = str(decrypt(ENCRYPTION_KEY, acg_request.sort_code)).replace("b", '').replace("'", '')
        acg_request.account_number = str(decrypt(ENCRYPTION_KEY, acg_request.account_number)).replace("b", '').replace("'", '')
    return render(request, 'dcac/view-request-admin.html', {'user': user,
                                                            'request': acg_request,
                                                            'items': items,
                                                            'receipts': receipts})


# ALL REQUESTS ADMIN
# Shows all previous requests.

@login_required(login_url='/accounts/login/')
def all_requests_admin(request):
    user = AdminUser.objects.get(user_id=request.user.username)
    requests = ACGReimbursementForm.objects.order_by('-form_id')
    return render(request, 'dcac/all-requests-admin.html', {'user': user,
                                                            'requests': requests})


# ADMIN PROFILE
# Allows admin to view/change their role.

@login_required(login_url='/accounts/login/')
def profile_admin(request):
    user = AdminUser.objects.get(user_id=request.user.username)
    return render(request, 'dcac/profile-admin.html', {'user': user})


# ERROR
# Returns error page, with message dependent on code.

def error(request, code):
    messages = {
        403: "Access Denied",
        404: "Page not found",
    }
    return render(request, 'roomballot/error.html', {'message': messages[code]})