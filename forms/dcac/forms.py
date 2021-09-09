from django import forms
from django.forms import widgets
from django.forms.widgets import NumberInput, RadioSelect, Textarea, TextInput
from .models import *
from forms.models import *
from .constants import *


class ACGReimbursementFormReceiptEntryClass(forms.ModelForm):
    class Meta:
        model = ACGReimbursementFormReceiptEntry
        fields = ['file']


class ACGReimbursementFormItemEntryClass(forms.ModelForm):
    class Meta:
        model = ACGReimbursementFormItemEntry
        fields = [
            'title',
            'amount',
            'description',
            'fund_source',
        ]

        labels = {
            'description': 'Description & Reasoning',
        }

        widgets = {
            'description': Textarea(attrs={'rows': 5}),
            'amount': NumberInput(attrs={"min": "0", "step": "0.01", "value": "0.00"}),
            'fund_source': RadioSelect,
        }


class ACGReimbursementFormClass(forms.ModelForm):
    class Meta:
        model = ACGReimbursementForm
        fields = [
            'organization',
            'reimbursement_type',

            'name_on_account',
            'sort_code',
            'account_number',
        ]

        labels = {
            'name_on_account': 'Account Holder'
        }

        widgets = {
            'name_on_account': TextInput(attrs={'placeholder': 'Mr Joe Bloggs'}),
            'sort_code': TextInput(attrs={'placeholder': '123456'}),
            'account_number': TextInput(attrs={'placeholder': '12345678'}),
        }


class ACGStandardForm(ACGReimbursementFormClass):
    """Form for standard requests."""


class ACGInternalForm(ACGReimbursementFormClass):
    """Form for internal requests. Does not need bank information"""
    class Meta(ACGReimbursementFormClass.Meta):
        exclude = ['name_on_account', 'sort_code', 'account_number']


class ACGLargeForm(ACGReimbursementFormClass):
    """Form for large requests. Does not need bank information"""
    class Meta(ACGReimbursementFormClass.Meta):
        exclude = ['name_on_account', 'sort_code', 'account_number']


ACG_FORMS = {
    'standard': (ACGStandardForm, RequestTypes.STANDARD),
    'internal': (ACGInternalForm, RequestTypes.INTERNAL),
    'large':    (ACGLargeForm, RequestTypes.LARGE),
}
