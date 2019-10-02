import json

from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from datetime import datetime
from .models import *


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

def dashboard(request):
    student = Student.objects.get(user_id=request.user.username)
    organizations = []
    organization_administrators = OrganizationAdministrator.objects.filter(student=student)
    for organization_administrator in organization_administrators:
        organizations.append(organization_administrator.organization)

    requests = ACGReimbursementForm.objects.filter(submitter=student.user_id).order_by('-form_id')[:3]

    return render(request, 'dcac/dashboard-student.html', {'organizations': organizations,
                                                           'can_make_new_request': len(organizations) > 0,
                                                           'requests': requests,
                                                           'student': student})


# ALL REQUESTS
# Allow student to view all requests they have made.

def all_requests(request):
    student = Student.objects.get(user_id=request.user.username)
    organizations = []
    organization_administrators = OrganizationAdministrator.objects.filter(student=student)
    for organization_administrator in organization_administrators:
        organizations.append(organization_administrator.organization)

    requests = ACGReimbursementForm.objects.filter(submitter=student.user_id).order_by('-form_id')
    return render(request, 'dcac/all-requests-student.html', {'student': student,
                                                              'requests': requests})


# VIEW REQUEST
# For student to view details of previous request.

def view_request(request, form_id):
    student = Student.objects.get(user_id=request.user.username)
    acg_request = get_object_or_404(ACGReimbursementForm, pk=form_id)
    items = ACGReimbursementFormItemEntry.objects.filter(form_id=acg_request)
    return render(request, 'dcac/view-request-student.html', {'student': student,
                                                              'request': acg_request,
                                                              'items': items})


# ACG FORM
# Allows student to fill out ACG reimbursement form.

def acg_form(request):
    student = Student.objects.get(user_id=request.user.username)
    if request.method == 'POST':
        file_entry = ACGReimbursementFormReceiptEntry()
        file_entry.file = request.FILES['receipt']
        file_entry.save()
        return HttpResponse(json.dumps({'receipt_id': file_entry.entry_id}), content_type="application/json")
    else:
        organizations = []
        organizationAdministrators = OrganizationAdministrator.objects.filter(student=student)
        for organizationAdministrator in organizationAdministrators:
            organizations.append(organizationAdministrator.organization)
        return render(request, 'dcac/acg-form-student.html', {'student': student,
                                                              'organizations': organizations})


# ACG FORM SUBMIT
# Allows submission of completed form.

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
        form.sort_code = sort_code
        form.account_number = account_number
        form.name_on_account = name_on_account
        form.submitter = student.user_id

        form.year = AcademicYear.objects.get(name="2019/20")
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

        return HttpResponse(json.dumps({'formId': form.form_id}), content_type="application/json")



# ADMIN VIEW REQUEST
# For admin to view details of request.

def view_request_admin(request, form_id):
    user = AdminUser.objects.get(user_id=request.user.username)
    acg_request = get_object_or_404(ACGReimbursementForm, pk=form_id)
    items = ACGReimbursementFormItemEntry.objects.filter(form=acg_request)
    receipts = ACGReimbursementFormReceiptEntry.objects.filter(form=acg_request)
    return render(request, 'dcac/view-request-admin.html', {'user': user,
                                                            'request': acg_request,
                                                            'items': items,
                                                            'receipts': receipts})


# ADMIN PROFILE
# Allows admin to view/change their role.

def profile_admin(request):
    user = AdminUser.objects.get(user_id=request.user.username)
    return render(request, 'dcac/profile-admin.html', {'user': user})