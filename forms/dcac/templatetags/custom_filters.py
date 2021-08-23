"""Custom filters used in Django Templates
To use in a template, add `{% load custom_filters %}` to the template"""

from django import template
from ..constants import *

register = template.Library()

@register.filter()
def str_reimbursement_type(request_type):
    return dict(RequestTypes.CHOICES).get(request_type, 'Standard')


@register.filter()
def str_fund_source(fund_source):
    return dict(FundSources.CHOICES).get(fund_source, 'Annual Consumable Grant')


@register.filter()
def str_budget_type(budget_type):
    return dict(BudgetType.CHOICES).get(budget_type, 'General Funding')