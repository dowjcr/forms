from django import forms
from django.forms import widgets
from django.forms.widgets import NumberInput, RadioSelect, Textarea, TextInput
from .models import *
from forms.models import *
from forms.constants import *

# BUDGET FORM

class BudgetForm(forms.ModelForm):
    """"""
    balance = forms.CharField(label='Rough Balance', required=False, widget=NumberInput(attrs={"min": "0", "step": "0.01", "placeholder": "0.00"}))

    class Meta:
        model = Budget
        fields = [
            'organization',
            'president',
            'president_crsid',
            'treasurer',
            'treasurer_crsid',
            'active_members',
            'subscription_details',

            'has_bank_account',
            'sort_code',
            'account_number',
            'name_of_bank',
            'balance',

            'comments',
        ]

        widgets = {
            'has_bank_account': RadioSelect,
            'subscription_details': Textarea(attrs={'rows':1}),
            'sort_code': TextInput(attrs={'placeholder': '123456'}),
            'account_number': TextInput(attrs={'placeholder': '12345678'}),

            'president_crsid': TextInput(attrs={'pattern': '[a-zA-Z0-9]+'}),
            'treasurer_crsid': TextInput(attrs={'pattern': '[a-zA-Z0-9]+'})
        }



class BudgetItemForm(forms.ModelForm):
    """"""
    amount = forms.CharField(widget=NumberInput(attrs={"min": "0", "step": "0.01", "value": "0.00"}))
    description = forms.CharField(label='Description & Reasoning', widget=Textarea(attrs={'rows': 5}))

    class Meta:
        model = BudgetItem
        fields = [
            'title',
            'budget_type',
        ]
