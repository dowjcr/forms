"""
EMAIL
Defines some methods to send email notifications to users.
Author Cameron O'Connor.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import AdminUser
import logging

FROM_EMAIL = "DCAC <no-reply@downingjcr.co.uk>"


# NOTIFY SENIOR TREASURER
# Invoked when form has been approved by junior treasurer.

def notify_senior_treasurer(form):
    subject = "New Reimbursement Request"
    recipient_list = [admin_user.user_id + "@cam.ac.uk" for admin_user in AdminUser.objects.filter(role=2)]
    html_message = render_to_string('dcac/emails/notify-treasurer.html', {'form': form})
    message = "A new reimbursement form has been submitted for your approval. Please go to the DCAC Reimbursement site."
    send_mail(subject, message, FROM_EMAIL, recipient_list, html_message=html_message)


# NOTIFY JUNIOR TREASURER
# Invoked when form is submitted.

def notify_junior_treasurer(form):
    subject = "New Reimbursement Request"
    recipient_list = [admin_user.user_id + "@cam.ac.uk" for admin_user in AdminUser.objects.filter(role=1)]
    html_message = render_to_string('dcac/emails/notify-treasurer.html', {'form': form})
    message = "A new reimbursement form has been submitted for your approval. Please go to the DCAC Reimbursement site."
    send_mail(subject, message, FROM_EMAIL, recipient_list, html_message=html_message)
