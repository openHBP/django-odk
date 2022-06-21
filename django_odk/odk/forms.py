# encoding:utf-8
from django import forms
from django.utils.translation import gettext as _
from .models import XForm


class OdkForm(forms.ModelForm):

    class Meta:
        model = XForm
        fields = ['xls_file', 'short_desc']
        widgets = {
            "xls_file": forms.FileInput(attrs={
                "accept": ".xlsx"}
            ),
            "short_desc": forms.TextInput(attrs={
                "class": "form-control"
            })
        }