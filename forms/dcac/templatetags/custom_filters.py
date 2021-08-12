from django import template
from ..constants import *

register = template.Library()

@register.filter()
def str_reimbursement_type(request_type):
    return dict(RequestTypes.CHOICES).get(request_type, 'Standard')