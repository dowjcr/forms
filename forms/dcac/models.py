"""
MODELS
Defines database models to be used in the DCAC forms application.
Author Cameron O'Connor
"""

from django.db import models


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
    ROLE_CHOICES = (
        (1, 'JCR Treasurer'),
        (2, 'Senior Treasurer'),
        (3, 'Bursary'),
    )

    user_id = models.CharField('CRSid', primary_key=True, max_length=10)
    first_name = models.CharField('First Name', max_length=50)
    surname = models.CharField('Surname', max_length=50)
    role = models.IntegerField('Role', choices=ROLE_CHOICES)

    def __str__(self):
        return str(self.first_name) + " " + str(self.surname)


# ORGANIZATION
# Represents an organization or society which is
# eligible for reimbursement.

class Organization(models.Model):
    organization_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    president = models.ForeignKey(Student, on_delete=models.SET_DEFAULT, default=None)
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
    rejected = models.BooleanField(default=False)
    name_on_account = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    sort_code = models.CharField(max_length=20)
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

    def __str__(self):
        return "Form " + str(self.form.form_id) + ", " + str(self.title)


# ACG REIMBURSEMENT FORM RECEIPT ENTRY
# Receipt to support a submitted ACG form.

class ACGReimbursementFormReceiptEntry(models.Model):
    entry_id = models.AutoField(primary_key=True)
    form = models.ForeignKey(ACGReimbursementForm, on_delete=models.SET_DEFAULT, default=None, null=True)
    file = models.FileField()
