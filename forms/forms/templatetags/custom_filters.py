"""Custom filters used in Django Templates
To use in a template, add `{% load custom_filters %}` to the template"""

from django import template
from django.conf import settings

from forms.constants import *
from dcac.constants import *
from budget.constants import *

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


@register.filter()
def str_academic_year(year):
    return f"{year}-{(year+1)%100}"


@register.filter()
def filter_budget_type(items, budget_type):
    """Filter a list of items to only those of a given type"""
    return items.filter(budget_type=budget_type)


@register.filter()
def add_strings(a, b):
    """Add two floats that are stored as strings"""
    return sum(map(float, (a, b)))


@register.filter()
def paginate_years(year):
    """Return a list of years for pagination"""
    START_YEAR = 2020 # first year that budgets were submitted using this system
    y = int(year)
    return (START_YEAR, False, y-1, y, y+1, False, settings.CURRENT_YEAR)