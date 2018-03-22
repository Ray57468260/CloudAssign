from django import forms

from .models import FileSimpleModel


class FileForm(forms.ModelForm):

    class Meta:
        model = FileSimpleModel
        fields = ('file', )
