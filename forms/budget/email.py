"""
EMAIL
Defines some methods to send email notifications to users.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import *
from forms.models import *
import logging
from django.conf import settings

from forms.constants import *
from forms.settings import notifier

def notify_budget_submit(budget):
    subject = "Budget Submitted"
    recipient_list = [user + "@cam.ac.uk" for user in (budget.submitter, budget.president_crsid, budget.treasurer_crsid)]
    html_message = render_to_string('budget/emails/budget-submitted.html', {'budget': budget})
    message = "A budget has been submitted for your society."
    notifier.SendEmail(recipients=recipient_list, subject=subject, bodyhtml=html_message, bodytext=message)


def notify_treasurer_budget(budget):
    subject = "Budget Submitted"
    recipient_list = [admin_user.user_id + "@cam.ac.uk" for admin_user in AdminUser.objects.filter(role=AdminRoles.JCRTREASURER)]
    html_message = render_to_string('budget/emails/budget-treasurer.html', {'budget': budget})
    message = "A budget has been submitted for a society. Please go to the DCAC Reimbursement site."
    notifier.SendEmail(recipients=recipient_list, subject=subject, bodyhtml=html_message, bodytext=message)

def notify_budget_approved(budget):
    subject = "Budget Approved"
    recipient_list = [user + "@cam.ac.uk" for user in (budget.submitter, budget.president_crsid, budget.treasurer_crsid)]
    html_message = render_to_string("budget/emails/budget-approved.html", {'budget': budget})
    message = "Your budget has been approved."
    notifier.SendEmail(recipients=recipient_list, subject=subject, bodyhtml=html_message, bodytext=message)

def notify_budget_amounts_edited(budget):
    subject = "Budget Amounts Edited"
    recipient_list = [user + "@cam.ac.uk" for user in (budget.submitter, budget.president_crsid, budget.treasurer_crsid)]
    html_message = render_to_string("budget/emails/budget-amounts-edited.html", {'budget': budget})
    message = "Your budget amounts have been edited."
    notifier.SendEmail(recipients=recipient_list, subject=subject, bodyhtml=html_message, bodytext=message)
