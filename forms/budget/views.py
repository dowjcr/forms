import json
import os
import re

from django.shortcuts import redirect
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.urls import reverse

from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, ModelFormMixin
from datetime import date

from .forms import *
from django.conf import settings
from forms.settings import CURRENT_YEAR
import logging

from .models import *
from forms.models import *
from forms.views import FormsStudentMixin, FormsAdminMixin
from dcac.models import ACGReimbursementForm

def SingleBudgetUsageContext(budget: Budget):
    budgetdata = {}
    pending_reimbursements = ACGReimbursementForm.get_budget_associated_reimbursements_pending(date=budget.date, organization_id=budget.organization)
    paid_reimbursements = ACGReimbursementForm.get_budget_associated_reimbursements_paid(date=budget.date, organization_id=budget.organization)
    all_reimbursements = ACGReimbursementForm.get_budget_associated_reimbursements_all(date=budget.date, organization_id=budget.organization)
    acg_pending_total = 0
    dep_pending_total = 0
    for pending_reimbursement in pending_reimbursements:
        acg_pending_total = acg_pending_total + pending_reimbursement.amount_acg()
        dep_pending_total = dep_pending_total + pending_reimbursement.amount_dep()
    acg_paid_total = 0
    dep_paid_total = 0
    for paid_reimbursement in paid_reimbursements:
        acg_paid_total = acg_paid_total + paid_reimbursement.amount_acg()
        dep_paid_total = dep_paid_total + paid_reimbursement.amount_dep()
    manual_acg_deduction, manual_dep_deduction = budget.get_total_manual_deductions()
    acg_paid_total = acg_paid_total + float(manual_acg_deduction)
    dep_paid_total = dep_paid_total + float(manual_dep_deduction)
    manual_adjustments = ManualAdjustment.objects.filter(budget=budget)
    budgetdata["manual_adjustments"] = manual_adjustments
    acg_total = acg_pending_total + acg_paid_total
    dep_total = dep_pending_total + dep_paid_total
    budgetdata["manual_acg_cost"] = float(manual_acg_deduction)
    budgetdata["manual_dep_cost"] = float(manual_dep_deduction)
    budgetdata["acg_total"] = acg_total
    budgetdata["dep_total"] = dep_total
    budgetdata["acg_paid_total"] = acg_paid_total
    budgetdata["dep_paid_total"] = dep_paid_total
    budgetdata["acg_pending_total"] = acg_pending_total
    budgetdata["dep_pending_total"] = dep_pending_total
    manual_acg_credit, manual_dep_credit = budget.get_total_manual_credits()
    dep_remaining = float(budget.amount_dep) + manual_dep_credit - float(dep_total)
    acg_remaining = float(budget.amount_acg) + manual_acg_credit -  float(acg_total)
    budgetdata["dep_remaining"] = dep_remaining
    budgetdata["acg_remaining"] = acg_remaining
    acg_budget = budget.amount_acg_float() + manual_acg_credit
    dep_budget = budget.amount_dep_float() + manual_dep_credit
    budgetdata["acg_budget"] = acg_budget
    budgetdata["dep_budget"] = dep_budget
    budgetdata["budget"] = budget
    budgetdata["reimbursements"] = all_reimbursements
    if float(budget.amount_dep) != 0:
        budgetdata["dep_centre_colour"] = '#1eb253'
        budgetdata["remaining_dep_message"] = "£{0:.2f} remaining of £{1:.2f} ({2:.1f}%)".format(dep_remaining, dep_budget, ((float(budget.amount_dep) - float(dep_total)) / float(budget.amount_dep) ) * 100)
    if float(budget.amount_acg) != 0:
        budgetdata["acg_centre_colour"] = '#1eb253'
        budgetdata["remaining_acg_message"] = "£{0:.2f} remaining of £{1:.2f} ({2:.1f}%)".format(acg_remaining, acg_budget, ((float(budget.amount_acg) - float(acg_total)) / float(budget.amount_acg) ) * 100)
    if float(budget.amount_dep) - float(dep_total) <= 0:
        budgetdata["dep_remaining"] = 0
        budgetdata["remaining_dep_message"] = "No funds remaining"
        budgetdata["dep_centre_colour"] = '#ea3323'
    if float(budget.amount_acg) - float(acg_total) <= 0:
        budgetdata["acg_remaining"] = 0
        budgetdata["remaining_acg_message"] = "No funds remaining"
        budgetdata["acg_centre_colour"] = '#ea3323'

    return budgetdata
def BudgetUsageContext(budget: Budget):
    budgetdata = {}
    pending_reimbursements = ACGReimbursementForm.get_budget_associated_reimbursements_pending(date=budget.date, organization_id=budget.organization)
    paid_reimbursements = ACGReimbursementForm.get_budget_associated_reimbursements_paid(date=budget.date, organization_id=budget.organization)
    acg_pending_total = 0
    dep_pending_total = 0
    for pending_reimbursement in pending_reimbursements:
        acg_pending_total = acg_pending_total + pending_reimbursement.amount_acg()
        dep_pending_total = dep_pending_total + pending_reimbursement.amount_dep()
    acg_paid_total = 0
    dep_paid_total = 0
    manual_acg_cost, manual_dep_cost = budget.get_total_manual_deductions()
    acg_paid_total = acg_paid_total + float(manual_acg_cost)
    dep_paid_total = dep_paid_total + float(manual_dep_cost)
    for paid_reimbursement in paid_reimbursements:
        acg_paid_total = acg_paid_total + paid_reimbursement.amount_acg()
        dep_paid_total = dep_paid_total + paid_reimbursement.amount_dep()
    acg_total = acg_pending_total + acg_paid_total
    dep_total = dep_pending_total + dep_paid_total
    budgetdata["acg_total"] = acg_total
    budgetdata["dep_total"] = dep_total
    budgetdata["acg_paid_total"] = acg_paid_total
    budgetdata["dep_paid_total"] = dep_paid_total
    budgetdata["acg_pending_total"] = acg_pending_total
    budgetdata["dep_pending_total"] = dep_pending_total
    manual_acg_credit, manual_dep_credit = budget.get_total_manual_credits()
    dep_remaining = float(budget.amount_dep) + manual_dep_credit - float(dep_total)
    acg_remaining = float(budget.amount_acg) + manual_acg_credit -  float(acg_total)
    budgetdata["dep_remaining"] = dep_remaining
    budgetdata["acg_remaining"] = acg_remaining
    acg_budget = budget.amount_acg_float() + manual_acg_credit
    dep_budget = budget.amount_dep_float() + manual_dep_credit
    budgetdata["acg_budget"] = acg_budget
    budgetdata["dep_budget"] = dep_budget
    budgetdata["budget"] = budget
    budgetdata["reimbursements"] = pending_reimbursements
    if float(budget.amount_acg) - float(acg_total) <= 0:
        budgetdata["acg_remaining"] = 0
    if float(budget.amount_dep) - float(dep_total) <= 0:
        budgetdata["dep_remaining"] = 0
    
    return budgetdata

# --- STUDENT VIEWS ---

class AllBudgetsView(ListView, FormsStudentMixin):
    """View a list of all budgets for which the student submitted, or is the president/treasurer of the society"""
    template_name = 'budget/all-budgets-student.html'
    context_object_name = 'budgets'

    def get_queryset(self):
        return all_budgets_for_student(self.student.user_id).order_by('-year', 'organization')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allow_budget_submit'] = settings.ALLOW_BUDGET_SUBMIT,
        
        return context


class DetailBudgetView(DetailView, FormsStudentMixin):
    """View the details of a submitted budget"""
    template_name = 'budget/view-budget-student.html'
    model = Budget
    pk_url_kwarg = 'budget_id'

    def get(self, request, *args, **kwargs):
        budget = super().get_object()

        if not budget.student_can_edit(self.student.user_id):
            raise PermissionDenied

        # enable editing - if the budget is still a draft, redirect to the update form view
        if not budget.submitted and settings.ALLOW_BUDGET_SUBMIT:
            return redirect('edit-budget', budget_id=kwargs['budget_id'])

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        items = self.object.get_items_as_json()
        context['existingItems'] = items

        return context


class SubmitBudgetMixin(ModelFormMixin):
    """Mixin for handling budget viewing authorisation, and item handling from submitted budget"""
    form_class = Budget

    def dispatch(self, request, *args, **kwargs):
        """Only allow edit while budgets submissions are enabled"""
        if not settings.ALLOW_BUDGET_SUBMIT:
            #TODO
            return redirect('view-budget')
        
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.kwargs['submitted'] = 'finish_button' in request.POST
        return super().post(request, *args, **kwargs)

    def get_object(self):
        """Only allow students with permission to edit"""
        budget = super().get_object()
        
        if not budget.student_can_edit(self.student.user_id):
            raise PermissionDenied

        return budget

    def form_valid(self, form: BudgetForm):
        """After validation, save items to budget"""
        budget = form.instance
        budget.year = settings.CURRENT_YEAR
        budget.submitter = self.student.user_id
        budget.save()

        form.create_items_from_json(budget)
        form.remove_items_from_json()
        budget.update_totals()

        if self.kwargs['submitted']:
            budget.send_email()
            budget.submitted = True
        
        budget.save()
        return super().form_valid(form)

    def get_success_url(self):
        kwargs = {'budget_id': self.object.budget_id}
        return reverse('view-budget', kwargs=kwargs)


class UpdateBudgetView(UpdateView, SubmitBudgetMixin, FormsStudentMixin):
    """View for updating a draft of an existing budget that has not been submitted yet"""
    template_name = 'budget/budget-form-student.html'
    model = Budget
    form_class = BudgetForm
    
    pk_url_kwarg = 'budget_id'
    context_object_name = 'budget'

    # TODO: cannot get edit view after submission

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.object.get_items_as_json()
        item_form = BudgetItemForm()

        context['item_form'] = item_form
        context['existingItems'] = items
        context['draft'] = True

        return context


class CreateBudgetView(CreateView, SubmitBudgetMixin, FormsStudentMixin):
    """View for creating a new budget"""
    template_name = 'budget/budget-form-student.html'
    form_class = BudgetForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        item_form = BudgetItemForm()
        existing_budgets = Budget.budgets_from_year(settings.CURRENT_YEAR)

        context['item_form'] = item_form
        context['existingBudgets'] = existing_budgets
        
        return context

class SingleBudgetUsageView(TemplateView, FormsStudentMixin):
    template_name = 'budget/single-budget-usage-student.html'
    pk_url_kwarg = 'budget_id'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            budget = Budget.objects.get(budget_id=kwargs["budget_id"], year=CURRENT_YEAR, approved=True)
        except ObjectDoesNotExist:
            raise Http404()
        if self.student.user_id.lower() not in budget.treasurer_crsid and self.student.user_id.lower() not in budget.president_crsid:
            raise PermissionDenied()
        budgetdata = SingleBudgetUsageContext(budget)

        context["budgetdata"] = budgetdata
        return context

class BudgetUsageView(TemplateView, FormsStudentMixin):
    template_name = 'budget/budget-usage-student.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        budgets = Budget.approved_budgets_from_year_as_official(settings.CURRENT_YEAR, self.student.user_id)
        if len(budgets) == 0:
            return context
        data = []
        for budget in budgets:
            budgetdata = BudgetUsageContext(budget)
            data.append(budgetdata)
        context["data"] = data
        return context

# --- ADMIN VIEWS ---

class DetailBudgetAdminView(DetailView, FormsAdminMixin):
    """View a budget, and allow the treasurer to leave comments"""
    template_name = 'budget/view-budget-admin.html'
    model = Budget
    pk_url_kwarg = 'budget_id'
    context_object_name = 'budget'

    def post(self, request, *args, **kwargs):
        # handle comments made by Junior Treasurer
        comment = request.POST.get('comment')
        target = request.POST.get('target')
        amount_acg = request.POST.get('amount_acg')
        amount_dep = request.POST.get('amount_dep')
        budget = self.get_object()
        if target == 'budget':
            budget.treasurer_comments = comment
            budget.save()
            return HttpResponse(json.dumps({'target': target,'comment': comment}), content_type='application/json')

        if target == 'approve':
            if budget.submitted != True:
                return HttpResponse(status=400, content="Cannot approve a budget that is still a draft.")
            budget.requested_amount_acg, budget.requested_amount_dep = budget.requested_totals()
            budget.approved = True
            budget.amount_acg = amount_acg
            budget.amount_dep = amount_dep
            budget.save()
            budget.notify_approve()
            return redirect('/budget/admin/budget/' + str(budget.budget_id))
        
        if target == 'convertDraft':
            if budget.submitted != True:
                return HttpResponse(status=400, content="Cannot convert a draft to a draft!")
            budget.submitted = False
            budget.save()
            budget.notify_budget_convert_draft()
            return redirect('/budget/admin/budget/' + str(budget.budget_id))
        
        if target == "editAmounts":
            if budget.amount_dep == amount_dep and budget.amount_acg == amount_acg:
                return HttpResponse(status=400, content="Amounts are the same as previously")
            budget.old_amount_acg = budget.amount_acg
            budget.old_amount_dep = budget.amount_dep
            budget.amount_acg = amount_acg
            budget.amount_dep = amount_dep
            budget.requested_amount_acg, budget.requested_amount_dep = budget.requested_totals()
            budget.save()
            budget.notify_budget_amounts_edited()
            return redirect('/budget/admin/budget/' + str(budget.budget_id))

        else:
            item = BudgetItem.objects.get(pk=target)
            item.treasurer_comments = comment
            item.save()
            return HttpResponse(json.dumps({'target': target,'comment': comment}), content_type='application/json')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        items = self.object.get_items_as_json()
        context['existingItems'] = items

        return context


class AllBudgetsAdminView(ListView, FormsAdminMixin):
    """View a list of all budgets for a given year"""
    template_name = 'budget/all-budgets-admin.html'
    ordering = ['organization']
    context_object_name = 'budgets'

    page_kwarg = 'year'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        self.kwargs.setdefault('year', settings.CURRENT_YEAR)
        return Budget.objects.filter(year=self.kwargs['year']).order_by("-approved", "-submitted", "organization__name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        organizations = Organization.objects.exclude(budget__year=self.kwargs['year'])

        context['year'] = self.kwargs['year']
        context['remaining_organizations'] = organizations
        context['allow_budget_submit'] = settings.ALLOW_BUDGET_SUBMIT

        return context
    
class SingleBudgetUsageAdminView(TemplateView, FormsAdminMixin):
    template_name = 'budget/single-budget-usage-admin.html'
    pk_url_kwarg = 'budget_id'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            budget = Budget.objects.get(budget_id=kwargs["budget_id"], year=CURRENT_YEAR, approved=True)
        except ObjectDoesNotExist:
            raise Http404()
        budgetdata = SingleBudgetUsageContext(budget)

        context["budgetdata"] = budgetdata
        return context

class BudgetUsageAdminView(TemplateView, FormsAdminMixin):
    template_name = 'budget/budget-usage-admin.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        budgets = Budget.approved_budgets_from_year(settings.CURRENT_YEAR)
        if len(budgets) == 0:
            return context
        data = []
        for budget in budgets:
            budgetdata = BudgetUsageContext(budget)
            data.append(budgetdata)
        context["data"] = data
        return context
    
class AddManualCostAdminView(View, FormsAdminMixin):
    def post(self, request, *args, **kwargs):
        reason = request.POST.get('reason')
        amount = request.POST.get('amount')
        if not re.fullmatch(r'[0-9]{1,6}(\.[0-9]{1,2})?', amount):
            return HttpResponse(content="NO")
        type = request.POST.get('type')
        if type == '0':
            amount = 0 - float(amount) 

        source = request.POST.get('source')
        budget = request.POST.get('budget')
        ManualAdjustment.objects.create(reason=reason, amount=amount, fund_source=source,added_by=self.user.user_id, budget=Budget.objects.get(budget_id=budget), date=date.today())
        return redirect("/budget/admin/usage/" + budget + "/")
    
class DeleteManualCostAdminView(View, FormsAdminMixin):
    def post(self, request, *args, **kwargs):
        manual_cost_id = request.POST.get("manual_adjustment_id")
        budget = request.POST.get('budget')
        manualcost = ManualAdjustment.objects.get(id=manual_cost_id)
        manualcost.delete()
        return redirect("/budget/admin/usage/" + budget + "/")