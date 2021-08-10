from django import forms
from django.forms.widgets import NumberInput, Textarea, TextInput
from .models import ACGReimbursementForm, ACGReimbursementFormItemEntry, ACGReimbursementFormReceiptEntry

class UploadReceiptForm(forms.ModelForm):
    file = forms.FileField(required=False)
    class Meta:
        model = ACGReimbursementFormReceiptEntry
        fields = []


class ACGReimbursementFormItemEntryClass(forms.ModelForm):
    title = forms.CharField(required=True)
    amount = forms.CharField(required=True, widget=NumberInput(attrs={'step': "1", "min": "0", "value": "0.00"}))
    description = forms.CharField(required=True, label='Description & Reasoning', widget=Textarea(attrs={'rows': 5}))

    class Meta:
        model = ACGReimbursementFormItemEntry
        fields = [
        ]

        

class ACGReimbursementFormClass(forms.ModelForm):
    raw_sort_code = forms.CharField(label='Sort Code', min_length=6, max_length=6, widget=TextInput(attrs={'placeholder': '123456'}))
    raw_account_number = forms.CharField(label='Account Number', min_length=8, max_length=8, widget=TextInput(attrs={'placeholder': '12345678'}))
    
    class Meta:
        model = ACGReimbursementForm
        fields = [
            'organization',
            'name_on_account',
        ]

        labels = {
            'name_on_account': 'Account Holder'
        }

        

