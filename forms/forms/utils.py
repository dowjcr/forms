"""Utility functions to be used across all apps"""

from django.core.exceptions import PermissionDenied

def user_or_403(request, model):
    try:
        return model.objects.get(user_id=request.user.username)
    except:
        raise PermissionDenied