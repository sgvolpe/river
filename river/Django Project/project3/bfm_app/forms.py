from django import forms
from . import models


class bfm_rsForm(forms.ModelForm):
    class Meta:
        fields = ("id", "title", 'bfml_file')
        model = models.bfm_rs

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("id", None)
        super().__init__(*args, **kwargs)
