from django import forms
from django.forms import widgets
from django.forms.widgets import NumberInput, RadioSelect, Textarea, TextInput
from .models import ACGReimbursementForm, ACGReimbursementFormItemEntry, ACGReimbursementFormReceiptEntry
from .constants import *

class UploadReceiptForm(forms.ModelForm):
    file = forms.FileField(required=False)
    class Meta:
        model = ACGReimbursementFormReceiptEntry
        fields = []


class ACGReimbursementFormItemEntryClass(forms.ModelForm):
    title = forms.CharField()
    amount = forms.CharField(widget=NumberInput(attrs={'step': "1", "min": "0", "value": "0.00"}))
    description = forms.CharField(label='Description & Reasoning', widget=Textarea(attrs={'rows': 5}))

    class Meta:
        model = ACGReimbursementFormItemEntry
        fields = [
            'fund_source',
        ]

        widgets = {
            'fund_source': RadioSelect
        }

        

class ACGReimbursementFormClass(forms.ModelForm):
    raw_sort_code = forms.CharField(label='Sort Code', min_length=6, max_length=6, widget=TextInput(attrs={'placeholder': '123456'}))
    raw_account_number = forms.CharField(label='Account Number', min_length=8, max_length=8, widget=TextInput(attrs={'placeholder': '12345678'}))
        
    class Meta:
        model = ACGReimbursementForm
        fields = [
            'organization',
            'name_on_account',
            'reimbursement_type',
        ]

        labels = {
            'name_on_account': 'Account Holder'
        }


class ACGStandardForm(ACGReimbursementFormClass):
    """"""


class ACGInternalForm(ACGReimbursementFormClass):
    """Form for internal requests. Does not need bank information"""
    raw_sort_code = None
    raw_account_number = None

    class Meta(ACGReimbursementFormClass.Meta):
        exclude = ['name_on_account']


class ACGLargeForm(ACGReimbursementFormClass):
    """Form for large requests. Does not need bank information"""
    raw_sort_code = None
    raw_account_number = None

    class Meta(ACGReimbursementFormClass.Meta):
        exclude = ['name_on_account']


ACG_FORMS = {
    'standard': (ACGStandardForm, RequestTypes.STANDARD),
    'internal': (ACGInternalForm, RequestTypes.INTERNAL),
    'large':    (ACGLargeForm, RequestTypes.LARGE),
}

