"""
MODELS
Defines database models to be used in the DCAC forms application.
Author Cameron O'Connor
"""

from django.db import models
from django.conf import settings
from django.core import serializers

import json
from simplecrypt import encrypt, decrypt

from .constants import *
from fernet_fields import EncryptedCharField


# STUDENT
# Stores user information. Note that user_id
# corresponds to CRSid.

class Student(models.Model):
    user_id = models.CharField('CRSid', primary_key=True, max_length=10)
    first_name = models.CharField('First Name', max_length=50)
    surname = models.CharField('Surname', max_length=50)

    def __str__(self):
        return str(self.first_name) + " " + str(self.surname)


# ADMIN USER
# Stores admin user information. Note that user_id
# corresponds to CRSid.

class AdminUser(models.Model):
    user_id = models.CharField('CRSid', primary_key=True, max_length=10)
    first_name = models.CharField('First Name', max_length=50)
    surname = models.CharField('Surname', max_length=50)
    role = models.IntegerField('Role', choices=AdminRoles.CHOICES)

    def __str__(self):
        return str(self.first_name) + " " + str(self.surname)


# ORGANIZATION
# Represents an organization or society which is
# eligible for reimbursement.

class Organization(models.Model):
    class Meta:
        ordering = ['name']
    organization_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.name


# ACG REIMBURSEMENT FORM
# Record of submitted form.

class ACGReimbursementForm(models.Model):
    form_id = models.AutoField(primary_key=True)
    submitter = models.CharField(max_length=10)
    organization = models.ForeignKey(Organization, on_delete=models.SET_DEFAULT, default=None)
    date = models.DateField()
    amount = models.CharField(max_length=20)
    reimbursement_type = models.IntegerField(choices=RequestTypes.CHOICES, default=RequestTypes.STANDARD)
    rejected = models.BooleanField(default=False)
    name_on_account = models.CharField(max_length=100, null=True)
    account_number = models.BinaryField(max_length=1000, null=True)
    sort_code = models.BinaryField(max_length=1000, null=True)

    jcr_treasurer_approved = models.BooleanField(default=False)
    jcr_treasurer_comments = models.CharField(max_length=500, blank=True)
    jcr_treasurer_name = models.CharField(max_length=100)
    jcr_treasurer_date = models.DateField(null=True)

    senior_treasurer_approved = models.BooleanField(default=False)
    senior_treasurer_comments = models.CharField(max_length=500, blank=True)
    senior_treasurer_name = models.CharField(max_length=100)
    senior_treasurer_date = models.DateField(null=True)

    bursary_paid = models.BooleanField(default=False)
    bursary_date = models.DateField(null=True)

    def __str__(self):
        return "Request " + str(self.form_id) + ", " + str(self.organization)


# ACG REIMBURSEMENT FORM ITEM ENTRY
# Item entry for reimbursement, included in
# a submitted ACG form.

class ACGReimbursementFormItemEntry(models.Model):
    entry_id = models.AutoField(primary_key=True)
    form = models.ForeignKey(ACGReimbursementForm, on_delete=models.SET_DEFAULT, default=None)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    amount = models.CharField(max_length=20)
    fund_source = models.IntegerField(choices=FundSources.CHOICES, default=FundSources.ACG)


    def __str__(self):
        return "Form " + str(self.form.form_id) + ", " + str(self.title)


# ACG REIMBURSEMENT FORM RECEIPT ENTRY
# Receipt to support a submitted ACG form.

class ACGReimbursementFormReceiptEntry(models.Model):
    entry_id = models.AutoField(primary_key=True)
    form = models.ForeignKey(ACGReimbursementForm, on_delete=models.SET_DEFAULT, default=None, null=True)
    file = models.FileField()



# BUDGET FORM ENTRY

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
    account_number = EncryptedCharField('Account Number', max_length=8, blank=True)
    sort_code = EncryptedCharField('Sort Code', max_length=6, blank=True)
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
