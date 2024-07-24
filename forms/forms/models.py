"""
MODELS
Defines database models to be used in the DCAC forms application.
"""

from django.db import models
from django.conf import settings

from .constants import *


class Student(models.Model):
    """Stores user information. Note that user_id corresponds to CRSid."""
    user_id = models.CharField('CRSid', primary_key=True, max_length=10)
    first_name = models.CharField('First Name', max_length=50)
    surname = models.CharField('Surname', max_length=50)

    def __str__(self):
        return str(self.first_name) + " " + str(self.surname)


class AdminUser(models.Model):
    """Stores admin user information. Note that user_id corresponds to CRSid."""
    user_id = models.CharField('CRSid', primary_key=True, max_length=10)
    first_name = models.CharField('First Name', max_length=50)
    surname = models.CharField('Surname', max_length=50)
    role = models.IntegerField('Role', choices=AdminRoles.CHOICES)

    def __str__(self):
        return str(self.first_name) + " " + str(self.surname)

class OrganizationManager(models.Manager):
    """Manager to use organization name as a primary key"""
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Organization(models.Model):
    """Represents an organization or society which is eligible for reimbursement."""
    class Meta:
        ordering = ['name']

    organization_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    hidden = models.BooleanField(default=False)

    objects = OrganizationManager()

    def natural_key(self):
        return self.name

    def __str__(self):
        return self.name