"""
MODELS
Defines database models to be used in the DCAC forms application.
Author Cameron O'Connor
"""

from django.db import models
from django.conf import settings
from django.core import serializers
from django.db.models import Sum, Q

import json
from datetime import datetime

from forms.constants import *
from .constants import *
from fernet_fields import EncryptedCharField

from forms.models import Organization
from .email import *


class ACGReimbursementForm(models.Model):
    """Record of submitted form."""
    form_id = models.AutoField(primary_key=True)
    submitter = models.CharField(max_length=10)
    organization = models.ForeignKey(Organization, on_delete=models.SET_DEFAULT, default=None)
    date = models.DateField()
    amount = models.CharField(max_length=20)
    reimbursement_type = models.IntegerField(choices=RequestTypes.CHOICES, default=RequestTypes.STANDARD)
    rejected = models.BooleanField(default=False)

    name_on_account = models.CharField(max_length=100, null=True)
    account_number = EncryptedCharField('Account Number', max_length=8, blank=True, null=True)
    sort_code = EncryptedCharField('Sort Code', max_length=6, blank=True, null=True)

    jcr_treasurer_approved = models.BooleanField(default=False)
    jcr_treasurer_comments = models.TextField(blank=True)
    jcr_treasurer_name = models.CharField(max_length=100)
    jcr_treasurer_date = models.DateField(null=True)

    senior_treasurer_approved = models.BooleanField(default=False)
    senior_treasurer_comments = models.TextField(blank=True)
    senior_treasurer_name = models.CharField(max_length=100)
    senior_treasurer_date = models.DateField(null=True)

    assistant_bursar_approved = models.BooleanField(default=False)
    assistant_bursar_comments = models.TextField(blank=True)
    assistant_bursar_name = models.CharField(max_length=100, null=True)
    assistant_bursar_date = models.DateField(null=True)

    bursary_paid = models.BooleanField(default=False)
    bursary_date = models.DateField(null=True)


    # -- STATIC METHODS ---
    @staticmethod
    def admin_to_action(role):
        """Returns a query set of all requests that require action from the given admin user"""
        if role == AdminRoles.JCRTREASURER:
            query = Q(rejected=False, jcr_treasurer_approved=False)
        elif role == AdminRoles.SENIORTREASURER:
            query = Q(rejected=False, jcr_treasurer_approved=True, senior_treasurer_approved=False)
        elif role == AdminRoles.BURSARY:
            query = Q(jcr_treasurer_approved=True, senior_treasurer_approved=True, bursary_paid=False) & \
                (~Q(reimbursement_type=RequestTypes.LARGE) | Q(assistant_bursar_approved=True))
        elif role == AdminRoles.ASSISTANTBURSAR:
            query = Q(rejected=False, jcr_treasurer_approved=True, senior_treasurer_approved=True, assistant_bursar_approved=False) & \
                Q(reimbursement_type=RequestTypes.LARGE)
        else:
            query = Q(form_id=-1) # empty query
    
        requests = ACGReimbursementForm.objects.filter(query).order_by('form_id')
        return requests

    # --- INSTANCE METHODS ---
    def update_amount(self):
        """Update the amount of the reimbursement based on the sum of all items"""
        self.amount = ACGReimbursementFormItemEntry.objects.filter(form=self).aggregate(Sum('amount'))['amount__sum']
        self.save()

    # Admin response handling
    
    def handle_admin_response(self, code, user, comments):
        """Calls function based on the response type `code`, and the role of the admin user"""
        if code == ResponseCodes.APPROVED:
            if user.role == AdminRoles.JCRTREASURER:
                self.jcr_treasurer_response(user, comments, approved=True)
            elif user.role == AdminRoles.SENIORTREASURER:
                self.senior_treasurer_response(user, comments, approved=True)
            elif user.role == AdminRoles.ASSISTANTBURSAR:
                self.assistant_bursar_response(user, comments, approved=True)

        elif code == ResponseCodes.REJECTED:
            self.clear_bank_details()
            notify_rejected(self)
            if user.role == AdminRoles.JCRTREASURER:
                self.jcr_treasurer_response(user, comments, approved=False)
            elif user.role == AdminRoles.SENIORTREASURER:
                self.senior_treasurer_response(user, comments, approved=False)
            elif user.role == AdminRoles.ASSISTANTBURSAR:
                self.assistant_bursar_response(user, comments, approved=False)

        elif code == ResponseCodes.PAID:
            self.clear_bank_details()
            self.bursary_response()
                    
        self.save()


    def jcr_treasurer_response(self, user, comments, approved):
        self.jcr_treasurer_approved = approved
        self.rejected = not approved
        self.jcr_treasurer_comments = comments
        self.jcr_treasurer_date = datetime.now()
        self.jcr_treasurer_name = str(user)

        if approved:
            notify_senior_treasurer(self)

    def senior_treasurer_response(self, user, comments, approved):
        self.senior_treasurer_approved = approved
        self.rejected = not approved
        self.senior_treasurer_comments = comments
        self.senior_treasurer_date = datetime.now()
        self.senior_treasurer_name = str(user)

        if approved:
            # only notify assistant bursar for large requests; otherwise notify bursary
            if self.reimbursement_type == RequestTypes.LARGE:
                notify_assistant_bursar(self)
            else:         
                notify_bursary(self)

    def assistant_bursar_response(self, user, comments, approved):
        self.assistant_bursar_approved = approved
        self.rejected = not approved
        self.assistant_bursar_comments = comments
        self.assistant_bursar_date = datetime.now()
        self.assistant_bursar_name = str(user)

        if approved:
            notify_bursary(self)

    def bursary_response(self):
        self.bursary_paid = True
        self.bursary_date = datetime.now()

        notify_paid(self)

    def clear_bank_details(self):
        self.sort_code = None
        self.account_number = None
        self.name_on_account = None

    def __str__(self):
        return "Request " + str(self.form_id) + ", " + str(self.organization)


class ACGReimbursementFormItemEntry(models.Model):
    """Item entry for reimbursement, included in a submitted ACG form."""
    entry_id = models.AutoField(primary_key=True)
    form = models.ForeignKey(ACGReimbursementForm, on_delete=models.SET_DEFAULT, default=None)
    title = models.CharField(max_length=100)
    description = models.TextField()
    amount = models.CharField(max_length=20)
    fund_source = models.IntegerField(choices=FundSources.CHOICES, default=FundSources.ACG)


    def __str__(self):
        return "Form " + str(self.form.form_id) + ", " + str(self.title)


class ACGReimbursementFormReceiptEntry(models.Model):
    """Receipt to support a submitted ACG form."""
    entry_id = models.AutoField(primary_key=True)
    form = models.ForeignKey(ACGReimbursementForm, on_delete=models.SET_DEFAULT, default=None, null=True)
    file = models.FileField(null=True)
