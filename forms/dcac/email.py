"""
EMAIL
Defines some methods to send email notifications to users.
Author Cameron O'Connor.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import *
from forms.models import *
import logging
from django.conf import settings

from forms.settings import notifier

from forms.constants import *

# NOTIFY BURSARY
# Invoked when form has been approved by senior treasurer.

def notify_bursary(form):
    subject = "New Reimbursement Request"
    recipient_list = [admin_user.user_id + "@cam.ac.uk" for admin_user in AdminUser.objects.filter(role=AdminRoles.BURSARY)]
    html_message = render_to_string('dcac/emails/notify-treasurer.html', {'form': form})
    message = "A new reimbursement form has been approved and is ready to be paid. Please go to the DCAC " \
              "Reimbursement site. "
    notifier.SendEmail(recipients=recipient_list, subject=subject, bodyhtml=html_message, bodytext=message)

# NOTiFY ASSISTANT BURSAR
# Invoked when form has been approved by senior treasurer, and must be approved by assistant bursar

def notify_assistant_bursar(form):
    subject = "New Reimbursement Request"
    recipient_list = [admin_user.user_id + "@cam.ac.uk" for admin_user in AdminUser.objects.filter(role=AdminRoles.ASSISTANTBURSAR)]
    html_message = render_to_string('dcac/emails/notify-treasurer.html', {'form': form})
    message = "A new reimbursement form has been submitted for your approval. Please go to the DCAC Reimbursement site."
    notifier.SendEmail(recipients=recipient_list, subject=subject, bodyhtml=html_message, bodytext=message)

# NOTIFY SENIOR TREASURER
# Invoked when form has been approved by junior treasurer.

def notify_senior_treasurer(form):
    subject = "New Reimbursement Request"
    recipient_list = [admin_user.user_id + "@cam.ac.uk" for admin_user in AdminUser.objects.filter(role=AdminRoles.SENIORTREASURER)]
    html_message = render_to_string('dcac/emails/notify-treasurer.html', {'form': form})
    message = "A new reimbursement form has been submitted for your approval. Please go to the DCAC Reimbursement site."
    notifier.SendEmail(recipients=recipient_list, subject=subject, bodyhtml=html_message, bodytext=message)


# NOTIFY JUNIOR TREASURER
# Invoked when form is submitted.

def notify_junior_treasurer(form):
    subject = "New Reimbursement Request"
    recipient_list = [admin_user.user_id + "@cam.ac.uk" for admin_user in AdminUser.objects.filter(role=AdminRoles.JCRTREASURER)]
    html_message = render_to_string('dcac/emails/notify-treasurer.html', {'form': form})
    message = "A new reimbursement form has been submitted for your approval. Please go to the DCAC Reimbursement site."
    notifier.SendEmail(recipients=recipient_list, subject=subject, bodyhtml=html_message, bodytext=message)

# NOTIFY REJECTED
# Invoked when form is rejected by a treasurer.

def notify_rejected(form):
    subject = "Reimbursement Request Rejected"
    recipient_list = [form.submitter + "@cam.ac.uk"]
    html_message = render_to_string('dcac/emails/rejected.html', {'form': form})
    message = "Unfortunately your recent DCAC reimbursement request has been rejected. Please go to the DCAC " \
              "Reimbursement site. "
    notifier.SendEmail(recipients=recipient_list, subject=subject, bodyhtml=html_message, bodytext=message)

# NOTIFY PAID
# Invoked when form is paid by the Bursary.

def notify_paid(form):
    subject = "Reimbursement Request Completed"
    recipient_list = [form.submitter + "@cam.ac.uk"]
    html_message = render_to_string('dcac/emails/paid.html', {'form': form})
    message = "Your DCAC Reimbursement request has been paid by the Bursary. Please note it may take a few working " \
              "days for the payment to clear. "
    notifier.SendEmail(recipients=recipient_list, subject=subject, bodyhtml=html_message, bodytext=message)
