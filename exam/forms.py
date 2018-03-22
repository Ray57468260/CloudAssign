from django import forms
from django.forms import ModelForm
from .models import *


class ChoiceForm(ModelForm):

    class Meta:
        model = Choice
        fields = ['courseID', 'is_single', 'descri', 'A',
                  'B', 'C', 'D', 'E', 'F', 'answer']
        widgets = {'courseID': forms.HiddenInput(
        ), 'is_single': forms.HiddenInput(), }


class JudgeForm(ModelForm):

    class Meta:
        model = Judge
        fields = ['courseID', 'descri', 'answer']
        widgets = {'courseID': forms.HiddenInput()}


class S_answerForm(ModelForm):

    class Meta:
        model = S_answer
        fields = ['courseID', 'descri', 'answer']
        widgets = {'courseID': forms.HiddenInput()}


class BlankForm(ModelForm):

    class Meta:
        model = Blank
        fields = ['courseID', 'descri', 'blank1', 'blank2',
                  'blank3', 'blank4', 'blank5', 'blank6']
        widgets = {'courseID': forms.HiddenInput()}


class BankProcessForm(ModelForm):

    class Meta:
        model = BankProcess
        fields = ['user_id', 'courseID', 'e_type', 'file']


class DocxForm(forms.Form):
    file = forms.FileField()


class DraftForm(ModelForm):

    class Meta:
        model = Draft
        fields = ['courseID', 'title', 'intro', 'draft_string']

    def __init__(self, *args, **kwargs):
        super(DraftForm, self).__init__(*args, **kwargs)
        self.fields['draft_string'].required = False
