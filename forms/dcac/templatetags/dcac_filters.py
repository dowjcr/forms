"""Custom filters used in DCAC Django Templates
To use in a template, add `{% load dcac_filters %}` to the template"""

from django import template
from django.conf import settings

from forms.constants import *
from dcac.constants import *
from budget.constants import *

from forms.models import AdminUser
from dcac.models import ACGReimbursementForm

register = template.Library()

@register.filter()
def view_admin_action(user: AdminUser, request: ACGReimbursementForm):
    """Show admin options if the current user's action is required for this reimbursement request"""
    return request in ACGReimbursementForm.admin_to_action(user.role)