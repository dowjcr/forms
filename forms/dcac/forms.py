from django import forms

class UploadReceiptForm(forms.Form):
    file = forms.FileField()