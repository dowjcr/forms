from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings as django_settings
from django.db import transaction


# LANDING PAGE
# Shown to user if they are not already authenticated
# using Raven.

def landing(request):
    if not request.user.is_authenticated:
        return render(request, 'dcac/landing.html')
    else:
        return HttpResponseRedirect('/dcac/dashboard')