from django import forms

class AddNewSku(forms.Form):
    sku = forms.CharField(label='',max_length=200,required=False)
    