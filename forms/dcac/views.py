from django.shortcuts import redirect, render, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from datetime import datetime
import json
from simplecrypt import encrypt, decrypt

from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, ModelFormMixin
from forms.views import FormsStudentMixin, FormsAdminMixin

from .models import *
from forms.models import *

from .forms import *
from .email import *
from .constants import *
from forms.utils import *
from django.conf import settings
import logging


LOG_FILE = 'dcac.log'
ENCRYPTION_KEY = settings.ENCRYPTION_KEY
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


# --- STUDENT VIEWS ---

class AllRequestsView(ListView, FormsStudentMixin):
    """Allow student to view all requests they have made."""
    template_name = 'dcac/all-requests-student.html'
    context_object_name = 'requests'
    
    def get_queryset(self):
        return ACGReimbursementForm.objects.filter(submitter=self.student.user_id).order_by('-form_id')


class DetailRequestView(DetailView, FormsStudentMixin):
    """For student to view details of previous request."""
    template_name = 'dcac/view-request-student.html'
    context_object_name = 'request'
    pk_url_kwarg = 'form_id'
    model = ACGReimbursementForm

    def get_object(self):
        obj = super().get_object()
        if obj.submitter != self.student.user_id:
            raise PermissionDenied
        
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = ACGReimbursementFormItemEntry.objects.filter(form_id=self.object)
        return context
    

class AcgFormView(CreateView, FormsStudentMixin):
    """Allows student to fill out ACG reimbursement form."""
    template_name = 'dcac/acg-form-student.html'
    pk_url_kwarg = 'request_type'
    
    def post(self, request, *args, **kwargs):
        if 'is_receipt' in request.POST:
            receipt_form = ACGReimbursementFormReceiptEntryClass(request.POST, request.FILES)
            file_entry = receipt_form.save()
            return HttpResponse(json.dumps({'receipt_id': file_entry.entry_id}), content_type="application/json")

        else:
            self.kwargs['items'] = json.loads(request.POST.get('items'))
            self.kwargs['receipts'] = json.loads(request.POST.get('receipts'))
            return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        reimbursement = form.instance
        reimbursement.submitter = self.student.user_id
        reimbursement.date = datetime.now()
        
        reimbursement.save()

        for item in self.kwargs['items']:
            entry = ACGReimbursementFormItemEntry.objects.create(form=reimbursement, **item)
            entry.save()

        for receipt in self.kwargs['receipts']:
            entry = ACGReimbursementFormReceiptEntry.objects.get(entry_id=receipt)
            entry.form = reimbursement
            entry.save()

        reimbursement.update_amount()

        notify_junior_treasurer(reimbursement)

        return super().form_valid(form)

    def get_form_class(self):
        form_cls, reimbursement_type = ACG_FORMS[self.kwargs['request_type']]
        self.kwargs['reimbursement_type'] = reimbursement_type
        return form_cls

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['item_form'] = ACGReimbursementFormItemEntryClass()
        context['receipt_form'] = ACGReimbursementFormReceiptEntryClass()
        context['reimbursement_type'] = self.kwargs['reimbursement_type']

        return context

    def get_success_url(self):
        kwargs = {'form_id': self.object.form_id}
        return reverse('view-request', kwargs=kwargs)


# --- ADMIN VIEWS ---

class DetailRequestAdminView(DetailView, FormsAdminMixin):
    """"""
    template_name = 'dcac/view-request-admin.html'
    model = ACGReimbursementForm
    pk_url_kwarg = 'form_id'
    context_object_name = 'request'

    def post(self, request, *args, **kwargs):
        code = request.POST.get('code')
        comments = request.POST.get('comments')
        self.object.handle_admin_response(code, self.user, comments)

        return super().post(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = ACGReimbursementFormItemEntry.objects.filter(form=self.object)
        context['receipts'] = ACGReimbursementFormReceiptEntry.objects.filter(form=self.object)
        return context


class AllRequestsAdminView(ListView, FormsAdminMixin):
    """"""
    template_name = 'dcac/all-requests-admin.html'
    model = ACGReimbursementForm
    paginate_by = 50
    ordering = ['-form_id']
    context_object_name = 'requests'
