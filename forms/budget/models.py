"""
MODELS
Defines database models to be used in the DCAC forms application.
"""

from django.db import models
from django.conf import settings
from django.core import serializers

import json

from forms.constants import *
from fernet_fields import EncryptedCharField

from forms.models import Organization

class Budget(models.Model):
    """"""
    budget_id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    submitted = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    # `year` is the year that the budget was submitted
    # e.g. 2021 would be for the 2021-22 academic year 
    year = models.IntegerField()

    date = models.DateField(auto_now_add=True)
    submitter = models.CharField(max_length=10)
    amount_acg = models.CharField(max_length=20)
    amount_dep = models.CharField(max_length=20)

    president = models.CharField('President', max_length=100)
    president_crsid = models.CharField('CRSid', max_length=10)
    treasurer = models.CharField('Treasurer', max_length=100)
    treasurer_crsid = models.CharField('CRSid', max_length=10)
    active_members = models.PositiveIntegerField('Number of Active Members', default=0)
    subscription_details = models.CharField('Details of subscriptions received from members (if any)', max_length=300, blank=True)

    has_bank_account = models.BooleanField(choices=((True, 'Yes'), (False, 'No')), default=False)
    account_number = EncryptedCharField('Account Number', max_length=8, blank=True, null=True)
    sort_code = EncryptedCharField('Sort Code', max_length=6, blank=True, null=True)
    name_of_bank = models.CharField('Name of Bank', max_length=100, blank=True)
    balance = models.CharField('Rough Balance', max_length=20, blank=True)

    comments = models.TextField('Comments', blank=True)
    treasurer_comments = models.TextField('Treasurer Comments', blank=True)


    # --- CLASS METHODS ---
    def budgets_from_year(year):
        """Returns a dictionary of all of the existing budgets for a given year
        {`organization_id`: `budget_id`}"""
        budgets = Budget.objects.filter(year=year).values('organization', 'budget_id')
        budget_dict = {}
        for budget in budgets:
            org, budget_id = budget.values()
            budget_dict[org] = budget_id
        return budget_dict


    # --- INSTANCE METHODS ---
    def get_items_as_json(self):
        """Returns all items for this budget as a json object"""
        items = {}
        for budget_type, budget_type_str in BudgetType.CHOICES:
            items_json = serializers.serialize('json', BudgetItem.objects.filter(budget_id=self.budget_id, budget_type=budget_type))
            items_dict = json.loads(items_json)
            items[budget_type_str] = [{'entry_id': item['pk'], **item['fields']} for item in items_dict]

        return items
        
    


# BUDGET ITEM
# A single item on a budget

class BudgetItem(models.Model):
    """"""
    entry_id = models.AutoField(primary_key=True)
    budget = models.ForeignKey(Budget, on_delete=models.SET_DEFAULT, default=None)
    
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    amount = models.CharField(max_length=20)
    budget_type = models.IntegerField(choices=BudgetType.CHOICES)

    treasurer_comments = models.TextField('Treasurer Comments', blank=True)
