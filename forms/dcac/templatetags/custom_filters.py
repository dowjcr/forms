from django import template
from ..constants import *

register = template.Library()

@register.filter()
def str_reimbursement_type(request_type):
    return dict(RequestTypes.CHOICES).get(request_type, 'Standard')


@register.filter()
def str_fund_source(fund_source):
    return dict(FundSources.CHOICES).get(fund_source, 'Standard')