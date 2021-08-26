import json

from django.shortcuts import redirect, render, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core import serializers
from django.core.exceptions import PermissionDenied
from datetime import datetime
from simplecrypt import encrypt, decrypt
from .models import *
from .forms import *
from .email import *
from .constants import *
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
    student = user_or_403(request, Student)

    requests = ACGReimbursementForm.objects.filter(submitter=student.user_id).order_by('-form_id')[:3]

    return render(request, 'dcac/dashboard-student.html', {'requests': requests,
                                                           'student': student})

# --- ACG REQUEST VIEWS ---
# ALL REQUESTS
# Allow student to view all requests they have made.

@login_required(login_url='/accounts/login/')
def all_requests(request):
    student = user_or_403(request, Student)
    requests = ACGReimbursementForm.objects.filter(submitter=student.user_id).order_by('-form_id')
    return render(request, 'dcac/all-requests-student.html', {'student': student,
                                                              'requests': requests})


# VIEW REQUEST
# For student to view details of previous request.

@login_required(login_url='/accounts/login/')
def view_request(request, form_id):
    student = user_or_403(request, Student)
    acg_request = get_object_or_404(ACGReimbursementForm, pk=form_id)
    items = ACGReimbursementFormItemEntry.objects.filter(form_id=acg_request)
    return render(request, 'dcac/view-request-student.html', {'student': student,
                                                              'request': acg_request,
                                                              'items': items})


# ACG FORM
# Allows student to fill out ACG reimbursement form.

@login_required(login_url='/accounts/login/')
def acg_form(request, request_type):
    student = user_or_403(request, Student)
    if request.method == 'POST':
        file_entry = ACGReimbursementFormReceiptEntry()
        file_entry.file = request.FILES['receipt']
        file_entry.save()
        return HttpResponse(json.dumps({'receipt_id': file_entry.entry_id}), content_type="application/json")
    else:
        cls, reimbursement_type = ACG_FORMS[request_type]
        reimbursement_form = cls()
        item_form = ACGReimbursementFormItemEntryClass()
        receipt_form = UploadReceiptForm()
        
        return render(request, 'dcac/acg-form-student.html', {'student': student,
                                                              'form': reimbursement_form,
                                                              'item_form': item_form,
                                                              'receipt_form': receipt_form,
                                                              'reimbursement_type': reimbursement_type})

# ACG FORM SUBMIT
# Allows submission of completed form.

@login_required(login_url='/accounts/login/')
def acg_form_submit(request):
    student = user_or_403(request, Student)
    if request.method == 'POST':
        reimbursement_type = int(request.POST.get('reimbursement_type'))
        reimbursement_type_name = dict(RequestTypes.CHOICES)[reimbursement_type]
        form_cls = ACG_FORMS[reimbursement_type_name.lower()][0]
        form = form_cls(request.POST)

        if form.is_valid():
            reimbursement = form.save(commit=False)

            items = json.loads(request.POST.get('items'))
            receipts = json.loads(request.POST.get('receipts'))

            reimbursement.date = datetime.now()
            if 'raw_sort_code' in form.cleaned_data:
                reimbursement.sort_code = encrypt(ENCRYPTION_KEY, form.cleaned_data['raw_sort_code'])
                reimbursement.account_number = encrypt(ENCRYPTION_KEY, form.cleaned_data['raw_account_number'])
            reimbursement.submitter = student.user_id

            total = 0
            reimbursement.save()

            for item in items:
                total += float(item['amount'])
                entry = ACGReimbursementFormItemEntry()
                entry.form = reimbursement
                entry.title = item['title']
                entry.description = item['description']
                entry.amount = item['amount']
                entry.fund_source = item['fund_source']
                entry.save()

            for receipt in receipts:
                entry = ACGReimbursementFormReceiptEntry.objects.get(entry_id=receipt)
                entry.form = reimbursement
                entry.save()

            reimbursement.amount = total
            reimbursement.save()

            notify_junior_treasurer(reimbursement)

            return redirect(f"/dcac/request/{reimbursement.form_id}")

    else:
        return redirect("/dcac/form/acg-standard")

# --- BUDGET VIEWS ---
# ALL BUDGETS

@login_required(login_url='/accounts/login/')
def all_budgets(request):
    student = user_or_403(request, Student)


# VIEW BUDGET
# If the budget has not been submitted, render the form with the existing information
# Otherwise display the budget

@login_required(login_url='/accounts/login/')
def view_budget(request, budget_id):
    student = user_or_403(request, Student)
    budget = get_object_or_404(Budget, pk=budget_id)
    items = BudgetItem.objects.filter(budget_id=budget_id)

    if budget.submitted or not settings.ALLOW_BUDGET_SUBMIT:
        return render(request, 'dcac/view-budget-student.html', {
            'student': student,
            'budget': budget,
            'items': items
            })

    else:
        # a draft has been created, and can be viewed by
        # the submitter, the treasurer, and the president
        if student.user_id not in (budget.submitter, budget.president_crsid, budget.treasurer_crsid):
            raise PermissionDenied


        budget_form = BudgetForm(instance=budget)
        item_form = BudgetItemForm()
        existing_items = {}
        for budget_type, budget_type_str in BudgetType.CHOICES:
            items_json = serializers.serialize('json', BudgetItem.objects.filter(budget_id=budget_id, budget_type=budget_type))
            items_dict = json.loads(items_json)
            existing_items[budget_type_str] = [{'entry_id': item['pk'], **item['fields']} for item in items_dict]
        
        return render(request, 'dcac/budget-form-student.html', {
            'student': student,
            'form': budget_form,
            'item_form': item_form,
            'existingItems': existing_items,
            'draft': True
            })


# BUDGET FORM

@login_required(login_url='/accounts/login/')
def budget_form(request):
    if not settings.ALLOW_BUDGET_SUBMIT:
        pass
    student = user_or_403(request, Student)
    budget_form = BudgetForm()
    item_form = BudgetItemForm()
    
    current_year = datetime.now().year
    # orgs = Organization.objects.filter(budget__year=current_year).values()
    orgs = Budget.objects.filter(year=current_year, submitted=True).values()

    # print(orgs)
    # orgs = {'Club Name': #budget id from current_year}

    submitted_organizations = json.dumps({})
    return render(request, 'dcac/budget-form-student.html', {
        'student': student,
        'form': budget_form,
        'item_form': item_form,
        'submittedOrganizations': submitted_organizations
        })


# BUDGET FORM SUBMIT
# Allows submission of completed form.

@login_required(login_url='/accounts/login/')
def budget_form_submit(request):
    student = user_or_403(request, Student)
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        submitted = 'finish_button' in request.POST
        if form.is_valid():
            budget_from_form = form.save(commit=False)
            current_year = datetime.now().year

            # find if form already exists
            print(form.cleaned_data)
            budget, created = Budget.objects.update_or_create(
                organization=form.cleaned_data['organization'], year=current_year,
                defaults=form.cleaned_data
            )
            print(f"{created=}")
            # try:
            #     existing_budget = Budget.objects.get(organization=budget.organization, year=current_year)
            #     budget.
            # except Budget.DoesNotExist:
            #     budget.submitter = student.user_id
            #     budget.year = current_year
            if created:
                budget.submitter = student.user_id

            budget.submitted = submitted
            items = json.loads(request.POST.get('items'))
            total_acg = 0
            total_dep = 0

            budget.save()

            for items_of_type in items.values():
                for item in items_of_type:
                    # do not add items that have already been added
                    try:
                        if 'entry_id' not in item:
                            raise BudgetItem.DoesNotExist
                        budget_item = BudgetItem.objects.get(pk=item['entry_id'])
                    except BudgetItem.DoesNotExist:
                        budget_item = BudgetItem(**item)
                        budget_item.budget = budget


                    if item['budget_type'] == BudgetType.EXCEPTIONAL:
                        total_dep += float(item['amount'])
                    else:
                        total_acg += float(item['amount'])

                    budget_item.save()

            budget.amount_acg = total_acg
            budget.amount_dep = total_dep

            #TODO: bank account info
            budget.save()

            # For any items that were deleted, remove them from the database
            deleted_items = json.loads(request.POST.get('deletedItems'))
            for entry_id in deleted_items:
                BudgetItem.objects.filter(pk=entry_id).delete()

            return redirect(f'/dcac/budget/{budget.budget_id}')

    else:
        return redirect('/dcac/form/budget')


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
    return render(request, 'dcac/dashboard-admin.html', {'user': user,
                                                         'requests': requests})


# ADMIN VIEW REQUEST
# For admin to view details of request.

@login_required(login_url='/accounts/login/')
def view_request_admin(request, form_id):
    user = user_or_403(request, AdminUser)
    acg_request = get_object_or_404(ACGReimbursementForm, pk=form_id)
    if request.method == 'POST':
        # Clicked 'approve'.
        comments = request.POST.get('comments')
        if request.POST.get('code') == ResponseCodes.APPROVED:
            if user.role == AdminRoles.JCRTREASURER:
                acg_request.jcr_treasurer_approved = True
                acg_request.jcr_treasurer_comments = comments
                acg_request.jcr_treasurer_date = datetime.now()
                acg_request.jcr_treasurer_name = str(user)
                notify_senior_treasurer(acg_request)
            elif user.role == AdminRoles.SENIORTREASURER:
                acg_request.senior_treasurer_approved = True
                acg_request.senior_treasurer_comments = comments
                acg_request.senior_treasurer_date = datetime.now()
                acg_request.senior_treasurer_name = str(user)

                # notify bursar for all requests; only notify assistant bursar for large requests
                if acg_request.reimbursement_type == RequestTypes.LARGE:
                    notify_assistant_bursar(acg_request)
                
                notify_bursary(acg_request)
            acg_request.save()
        # Clicked 'rejected'
        elif request.POST.get('code') == ResponseCodes.REJECTED:
            acg_request.rejected = True
            acg_request.sort_code = None
            acg_request.account_number = None
            acg_request.name_on_account = None
            if user.role == AdminRoles.JCRTREASURER:
                acg_request.jcr_treasurer_approved = False
                acg_request.jcr_treasurer_comments = comments
                acg_request.jcr_treasurer_date = datetime.now()
                acg_request.jcr_treasurer_name = str(user)
            elif user.role == AdminRoles.SENIORTREASURER:
                acg_request.senior_treasurer_approved = False
                acg_request.senior_treasurer_comments = comments
                acg_request.senior_treasurer_date = datetime.now()
                acg_request.senior_treasurer_name = str(user)
            acg_request.save()
            notify_rejected(acg_request)
        elif request.POST.get('code') == ResponseCodes.PAID:
            acg_request.bursary_paid = True
            acg_request.bursary_date = datetime.now()
            acg_request.account_number = None
            acg_request.sort_code = None
            acg_request.name_on_account = None
            acg_request.save()
            notify_paid(acg_request)
        return HttpResponse(json.dumps({'responseCode': 1}), content_type="application/json")

    items = ACGReimbursementFormItemEntry.objects.filter(form=acg_request)
    receipts = ACGReimbursementFormReceiptEntry.objects.filter(form=acg_request)

    if user.role in (AdminRoles.BURSARY, AdminRoles.ASSISTANTBURSAR) and not acg_request.bursary_paid and acg_request.sort_code is not None:
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
    user = user_or_403(request, AdminUser)
    requests = ACGReimbursementForm.objects.order_by('-form_id')
    return render(request, 'dcac/all-requests-admin.html', {'user': user,
                                                            'requests': requests})


# ADMIN PROFILE
# Allows admin to view/change their role.

@login_required(login_url='/accounts/login/')
def profile_admin(request):
    user = user_or_403(request, AdminUser)
    return render(request, 'dcac/profile-admin.html', {'user': user})


def user_or_403(request, model):
    try:
        return model.objects.get(user_id=request.user.username)
    except:
        raise PermissionDenied