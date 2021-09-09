from django import forms
from django.forms.widgets import NumberInput, RadioSelect, Textarea, TextInput, HiddenInput
import json
from .models import *
from forms.models import *
from forms.constants import *

from .email import notify_budget_submit, notify_treasurer_budget

# BUDGET FORM

class BudgetForm(forms.ModelForm):
    """"""
    balance = forms.CharField(label='Rough Balance', required=False, widget=NumberInput(attrs={"min": "0", "step": "0.01", "placeholder": "0.00"}))
    items = forms.CharField(required=False, widget=HiddenInput())
    deleted_items = forms.CharField(initial="[]", required=False, widget=HiddenInput())

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

    def send_email(self):
        budget = self.instance
        notify_budget_submit(budget)
        notify_treasurer_budget(budget)


    def create_items_from_json(self, budget):
        """Creates or updates items from the json output of form, in format
        {General: [], Cuppers: [], Exceptional: []}"""
        items = json.loads(self.cleaned_data['items'])
        for items_of_type in items.values():
            for item in items_of_type:
                defaults = {**item, 'budget': budget}
                print(defaults)
                if item.get('entry_id'):
                    BudgetItem.objects.update_or_create(
                        pk=item.get('entry_id'),
                        defaults=defaults
                        )
                else:
                    BudgetItem.objects.create(**defaults)

    def remove_items_from_json(self):
        """Deletes items from the budgetitem database according to a list of ids,
        [1, 2, 3, ...]"""
        deleted_items = json.loads(self.cleaned_data.get('deleted_items'))
        for entry_id in deleted_items:
            BudgetItem.objects.filter(pk=entry_id).delete()


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
