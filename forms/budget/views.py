from dcac.email import notify_budget_submit, notify_treasurer_budget
import json
from django.db.models.query_utils import Q

from django.shortcuts import redirect, render, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core import serializers
from django.core.exceptions import PermissionDenied
from datetime import datetime
from simplecrypt import encrypt, decrypt
from .models import *
from .forms import *
from .email import *
# from .constants import *
from django.conf import settings
import logging

from forms.utils import user_or_403
from .models import *
from forms.models import *
from dcac.models import *


# Create your views here.

# --- BUDGET VIEWS ---
# ALL BUDGETS

@login_required(login_url='/accounts/login/')
def all_budgets(request):
    student = user_or_403(request, Student)
    budgets = Budget.objects.filter(Q(submitter=student.user_id) | Q(president_crsid=student.user_id) | Q(treasurer_crsid=student.user_id))
    return render(request, 'budget/all-budgets-student.html', {
        'student': student,
        'budgets': budgets,
        'allow_budget_submit': settings.ALLOW_BUDGET_SUBMIT
    })


# VIEW BUDGET
# If the budget has not been submitted, render the form with the existing information
# Otherwise display the budget

@login_required(login_url='/accounts/login/')
def view_budget(request, budget_id):
    student = user_or_403(request, Student)
    budget = get_object_or_404(Budget, pk=budget_id)

    # a draft has been created, and can be viewed by
    # the submitter, the treasurer, and the president
    if student.user_id not in (budget.submitter, budget.president_crsid, budget.treasurer_crsid):
        raise PermissionDenied

    items = budget.get_items_as_json()

    if budget.submitted or not settings.ALLOW_BUDGET_SUBMIT:
        return render(request, 'budget/view-budget-student.html', {
            'student': student,
            'budget': budget,
            'existingItems': items
            })

    else:
        budget_form = BudgetForm(instance=budget)
        item_form = BudgetItemForm()
        
        return render(request, 'budget/budget-form-student.html', {
            'student': student,
            'form': budget_form,
            'item_form': item_form,
            'existingItems': items,
            'existingOrganization': budget.organization,
            'draft': True
            })


# BUDGET FORM

@login_required(login_url='/accounts/login/')
def budget_form(request, budget_form=None):
    if not settings.ALLOW_BUDGET_SUBMIT:
        return redirect('all-budgets')
    student = user_or_403(request, Student)
    
    if budget_form is None:
        budget_form = BudgetForm()
    
    item_form = BudgetItemForm()
    
    current_year = settings.CURRENT_YEAR
    existing_budgets = Budget.budgets_from_year(current_year)

    return render(request, 'budget/budget-form-student.html', {
        'student': student,
        'form': budget_form,
        'item_form': item_form,
        'existingBudgets': existing_budgets
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
            current_year = settings.CURRENT_YEAR
            # find if form already exists
            budget, created = Budget.objects.update_or_create(
                organization=form.cleaned_data['organization'], year=current_year,
                defaults=form.cleaned_data
            )

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
                    #TODO: use get_or_create
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

            budget.save()
            notify_budget_submit(budget)
            notify_treasurer_budget(budget)

            # For any items that were deleted, remove them from the database
            deleted_items = json.loads(request.POST.get('deletedItems'))
            for entry_id in deleted_items:
                BudgetItem.objects.filter(pk=entry_id).delete()

            return redirect('view-budget', budget.budget_id)

        else:
            return budget_form(request, budget_form=form)

    else:
        return redirect('budget-form')


# ADMIN VIEW BUDGET
# For admin to view the details of a budget

@login_required(login_url='/accounts/login/')
def view_budget_admin(request, budget_id):
    user = user_or_403(request, AdminUser)
    budget = get_object_or_404(Budget, pk=budget_id)
    
    # a comment has been added
    if request.method == 'POST':
        comment = request.POST.get('comment')
        target = request.POST.get('target')

        if target == 'budget':
            budget.treasurer_comments = comment
            budget.save()

        else:
            item = BudgetItem.objects.get(pk=target)
            item.treasurer_comments = comment
            item.save()

        return HttpResponse(json.dumps({'target': target,'comment': comment}), content_type='application/json')
        

    items = budget.get_items_as_json()

    return render(request, 'budget/view-budget-admin.html', {
        'user': user,
        'budget': budget,
        'existingItems': items,
    })

# ALL BUDGETS ADMIN
# Shows all previous budgets

@login_required(login_url='/accounts/login/')
def all_budgets_admin(request, year=None):
    user = user_or_403(request, AdminUser)
    if year is None: 
        year = settings.CURRENT_YEAR

    budgets = Budget.objects.filter(year=year).order_by('-year', 'organization') 
    organizations = Organization.objects.exclude(budget__year=year)

    return render(request, 'budget/all-budgets-admin.html', {
        'user': user,
        'budgets': budgets,
        'year': year,
        'remaining_organizations': organizations,
        'allow_budget_submit': settings.ALLOW_BUDGET_SUBMIT
    })