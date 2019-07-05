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
        return self.first_name + " " + self.surname


# ORGANIZATION
# Represents an organization or society which is
# eligible for reimbursement.

class Organization(models.Model):
    organization_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    president = models.ForeignKey(Student, on_delete=models.SET_DEFAULT, default=None)
    description = models.CharField(max_length=500)

    def __str__(self):
        return name


# BUDGET YEAR
# Represents an academic year for which a budget
# is valid.

class AcademicYear(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return name


# BUDGET ENTRY
# Represents a budget entry for an organization
# and budget year.

class BudgetEntry(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.SET_DEFAULT, default=None)
    year = models.ForeignKey(AcademicYear, on_delete=models.SET_DEFAULT, default=None)
    amount = models.FloatField()

    def __str__(self):
        return self.organization.__str__() + ", Year " + self.year.__str__()


# ACG REIMBURSEMENT FORM
# Record of submitted form.

class ACGReimbursementForm(models.Model):
    form_id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_DEFAULT, default=None)
    year = models.ForeignKey(AcademicYear, on_delete=models.SET_DEFAULT, default=None)
    date = models.DateField()
    name_on_account = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    sort_code = models.CharField(max_length=20)
    jcr_treasurer_approved = models.BooleanField(default=False)
    jcr_treasurer_comments = models.CharField(max_length=500)
    senior_treasurer_approved = models.BooleanField(default=False)
    senior_treasurer_comments = models.CharField(max_length=500)
    bursary_paid = models.BooleanField(default=False)

    def __str__(self):
        return "Request " + str(self.form_id) + ", " + self.organization.__str__()


# ACG REIMBURSEMENT FORM ITEM ENTRY
# Item entry for reimbursement, included in
# a submitted ACG form.

class ACGReimbursementFormItemEntry(models.Model):
    entry_id = models.AutoField(primary_key=True)
    form = models.ForeignKey(ACGReimbursementForm, on_delete=models.SET_DEFAULT, default=None)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)

    def __str__(self):
        return "Form " + str(self.form.form_id) + ", " + self.title


# ACG REIMBURSEMENT FORM RECEIPT ENTRY
# Receipt to support a submitted ACG form.

class ACGReimbursementFormReceiptEntry(models.Model):
    entry_id = models.AutoField(primary_key=True)
