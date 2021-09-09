# encoding:utf-8
from django import forms
from django.utils.translation import ugettext as _
from .models import XForm


class OdkForm(forms.ModelForm):

    class Meta:
        model = XForm
        fields = ['xml_file', 'short_desc']
        widgets = {
            "xml_file": forms.FileInput(attrs={
                "accept": ".xml"}
            ),
            "short_desc": forms.TextInput(attrs={
                "class": "form-control"
            })
        }

    # def __init__(self, uploaded_file_url):
    #     uploaded_file_url = kwargs.pop("uploaded_file_url", None)
    #     super().__init__(uploaded_file_url)
    #     self.fields["xml_file"].values = 'coucou'