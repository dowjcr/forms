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
from forms.templatetags.custom_filters import str_academic_year

def budget_recipient_crsid_list(budget):
    crsid_list = [budget.submitter]
    presidents = budget.president_crsid.split(",")
    crsid_list.extend(presidents)
    treasurer = budget.treasurer_crsid.split(",")
    crsid_list.extend(treasurer)
    return crsid_list

def notify_budget_submit(budget):
    subject = "{0} - {1} Budget Submitted".format(budget.organization.name, str_academic_year(budget.year))
    recipient_list = [user + "@cam.ac.uk" for user in budget_recipient_crsid_list(budget)]
    html_message = render_to_string('budget/emails/budget-submitted.html', {'budget': budget})
    message = "A budget has been submitted for your society."
    notifier.SendEmail(recipients=recipient_list, subject=subject, bodyhtml=html_message, bodytext=message)


def notify_treasurer_budget(budget):
    subject = "{0} - {1} Budget Submitted".format(budget.organization.name, str_academic_year(budget.year))
    recipient_list = [admin_user.user_id + "@cam.ac.uk" for admin_user in AdminUser.objects.filter(role=AdminRoles.JCRTREASURER)]
    html_message = render_to_string('budget/emails/budget-treasurer.html', {'budget': budget})
    message = "A budget has been submitted for a society. Please go to the DCAC Reimbursement site."
    notifier.SendEmail(recipients=recipient_list, subject=subject, bodyhtml=html_message, bodytext=message)

def notify_budget_approved(budget):
    subject = "{0} - {1} Budget Approved".format(budget.organization.name, str_academic_year(budget.year))
    recipient_list = [user + "@cam.ac.uk" for user in budget_recipient_crsid_list(budget)]
    html_message = render_to_string("budget/emails/budget-approved.html", {'budget': budget})
    message = "Your budget has been approved."
    notifier.SendEmail(recipients=recipient_list, subject=subject, bodyhtml=html_message, bodytext=message)

def notify_budget_amounts_edited(budget):
    subject = "{0} - {1} Budget Amounts Changed".format(budget.organization.name, str_academic_year(budget.year))
    recipient_list = [user + "@cam.ac.uk" for user in budget_recipient_crsid_list(budget)]
    html_message = render_to_string("budget/emails/budget-amounts-edited.html", {'budget': budget})
    message = "Your budget amounts have been changed."
    notifier.SendEmail(recipients=recipient_list, subject=subject, bodyhtml=html_message, bodytext=message)
