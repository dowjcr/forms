import json

from django.shortcuts import redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, ModelFormMixin

from .forms import *
from django.conf import settings
import logging

from .models import *
from forms.models import *
from forms.views import FormsStudentMixin, FormsAdminMixin


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
        budget = self.get_object()

        if target == 'budget':
            budget.treasurer_comments = comment
            budget.save()

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
        return Budget.objects.filter(year=self.kwargs['year'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        organizations = Organization.objects.exclude(budget__year=self.kwargs['year'])

        context['year'] = self.kwargs['year']
        context['remaining_organizations'] = organizations
        context['allow_budget_submit'] = settings.ALLOW_BUDGET_SUBMIT

        return context