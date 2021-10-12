"""forms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from .views import *

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', RedirectView.as_view(pattern_name='landing')),
    path('welcome/', LandingView.as_view(), name='landing'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('backend/', admin.site.urls),
    path('admin/', DashboardAdminView.as_view(), name='dashboard-admin'),
    path('admin/profile/', ProfileAdminView.as_view(), name='profile-admin'),

    path('dcac/', include('dcac.urls')),
    path('budget/', include('budget.urls')),
    path('api/', include('api.urls')),
    path(r'', include('ucamwebauth.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
