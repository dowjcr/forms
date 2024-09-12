"""Custom filters used in Budget Django Templates
To use in a template, add `{% load budget_filters %}` to the template"""

from django import template
from django.conf import settings

from forms.constants import *
from dcac.constants import *
from budget.constants import *


register = template.Library()

@register.filter()
def year_change(i, budgets):
    """Add table-border-bottom class to any budgets that seperate two different years"""
    return i < len(budgets) - 1 and budgets[i].year != budgets[i+1].year

@register.filter()
def fund_source_as_text(value):
    if value == 1:
        return "ACG"
    else:
        return "Depreciation"
    
@register.filter()
def remove_minus(value):
    if value < 0:
        return value * -1
    return value