"""
MODELS
Defines database models to be used in the DCAC forms application.
"""

from django.db import models
from django.conf import settings
from django.core import serializers
from django.forms import TextInput

import json

from django.db.models import Sum
from django.db.models.query_utils import Q

from forms.models import Organization
from forms.constants import *
from budget.constants import *
from budget.email import notify_budget_submit, notify_treasurer_budget, notify_budget_approved
from fernet_fields import EncryptedCharField


def all_budgets_for_student(user_id):
    """Returns a queryset for all budgets that a student can view/edit
    i.e. is the submitter, president, or treasurer for any of the organization's budgets"""
    query = Q(budget__submitter=user_id) | Q(budget__president_crsid=user_id) | Q(budget__treasurer_crsid=user_id)
    orgs = Organization.objects.filter(query)
    budgets = Budget.objects.filter(organization__in=orgs)
    return budgets


class CRSidField(models.CharField):
    """Text field for CRSid - automatic lowercase"""
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 10
        if not args:
            # arg[0] is the verbose name, if it exists
            kwargs.setdefault('verbose_name', 'CRSid')
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        """Convert to lowercase"""
        return str(value).lower()


class Budget(models.Model):
    """A budget submitted for a given `organization` for a single `year`"""
    budget_id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    submitted = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    # `year` is the year that the budget was submitted
    # e.g. 2021 would be for the 2021-22 academic year 
    year = models.IntegerField()

    date = models.DateField(auto_now_add=True)
    submitter = models.CharField(max_length=10)
    amount_acg = models.CharField(max_length=20, default='0')
    amount_dep = models.CharField(max_length=20, default='0')

    president = models.CharField('President', max_length=100)
    president_crsid = CRSidField()
    treasurer = models.CharField('Treasurer', max_length=100)
    treasurer_crsid = CRSidField()
    active_members = models.PositiveIntegerField('Number of Active Members', default=0)
    subscription_details = models.TextField('Details of subscriptions received from members (if any)', blank=True)

    has_bank_account = models.BooleanField(choices=((True, 'Yes'), (False, 'No')), default=False)
    account_number = EncryptedCharField('Account Number', max_length=8, blank=True, null=True)
    sort_code = EncryptedCharField('Sort Code', max_length=6, blank=True, null=True)
    name_of_bank = models.CharField('Name of Bank', max_length=100, blank=True)
    balance = models.CharField('Rough Balance', max_length=20, blank=True)

    comments = models.TextField('Comments', blank=True)
    treasurer_comments = models.TextField('Treasurer Comments', blank=True)


    # --- CLASS METHODS ---
    @staticmethod
    def budgets_from_year(year):
        """Returns a dictionary of all of the existing budgets for a given year
        {`organization_id`: `budget_id`}"""
        budgets = Budget.objects.filter(year=year).values('organization', 'budget_id')
        budget_dict = {}
        for budget in budgets:
            org, budget_id = budget.values()
            budget_dict[org] = budget_id
        return budget_dict

    @staticmethod
    def approved_budgets_from_year_as_official(year, student_crsid):
        """Returns the existing budgets for a given year where the given student is either the president or treasurer"""
        budgets = Budget.objects.filter(Q(year=year), Q(approved=True), Q(president_crsid = student_crsid) | Q(treasurer_crsid = student_crsid)).order_by("organization__name")
        return budgets
    
    @staticmethod
    def approved_budgets_from_year(year):
        """Returns the existing budgets for a given year"""
        budgets = Budget.objects.filter(Q(year=year), Q(approved=True)).order_by("organization__name")
        return budgets

    # --- INSTANCE METHODS ---
    def student_can_edit(self, user_id):
        return self in all_budgets_for_student(user_id)


    def get_items_as_json(self):
        """Returns all items for this budget as a json object"""
        items = {}
        for budget_type, budget_type_str in BudgetType.CHOICES:
            items_json = serializers.serialize('json', BudgetItem.objects.filter(budget_id=self.budget_id, budget_type=budget_type))
            items_dict = json.loads(items_json)
            items[budget_type_str] = [{'entry_id': item['pk'], **item['fields']} for item in items_dict]

        return items

    def update_totals(self):
        """Update the totals for the budget based on the sum of all items
        `or 0` ensures that the sum is a number even if no items of that type are in the budget"""
        budget_items = BudgetItem.objects.filter(budget=self)
        self.amount_acg = budget_items.exclude(budget_type=BudgetType.EXCEPTIONAL).aggregate(Sum('amount'))['amount__sum'] or 0
        self.amount_dep = budget_items.filter(budget_type=BudgetType.EXCEPTIONAL).aggregate(Sum('amount'))['amount__sum'] or 0
        self.save()

    def requested_totals(self):
        budget_items = BudgetItem.objects.filter(budget=self)
        amount_acg = budget_items.exclude(budget_type=BudgetType.EXCEPTIONAL).aggregate(Sum('amount'))['amount__sum'] or 0
        amount_dep = budget_items.filter(budget_type=BudgetType.EXCEPTIONAL).aggregate(Sum('amount'))['amount__sum'] or 0
        return float(amount_acg), float(amount_dep)

    def amount_acg_float(self):
        amount_acg_float = float(self.amount_acg)
        return amount_acg_float
    
    def amount_dep_float(self):
        amount_dep_float = float(self.amount_dep)
        return amount_dep_float
    
    def send_email(self):
        notify_budget_submit(self)
        notify_treasurer_budget(self)

    def notify_approve(self):
        notify_budget_approved(self)
        
    


# BUDGET ITEM
# A single item on a budget

class BudgetItem(models.Model):
    """An item submitted for a single `Budget`"""
    entry_id = models.AutoField(primary_key=True)
    budget = models.ForeignKey(Budget, on_delete=models.SET_DEFAULT, default=None)
    
    title = models.CharField(max_length=100)
    description = models.TextField('Description & Reasoning')
    amount = models.CharField(max_length=20)
    budget_type = models.IntegerField(choices=BudgetType.CHOICES)

    treasurer_comments = models.TextField('Treasurer Comments', blank=True)
