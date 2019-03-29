from django import forms
from django.forms import ModelForm
from .models import Question, Answer, Course


class AnswerForm(ModelForm):

    class Meta:
        model = Answer
        fields = ['questionID', 'user_id', 'subject', 'content',
                  'accepted', 'status', 'grade', 'suggestions', 'file']

    def __init__(self, *args, **kwargs):
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.fields['grade'].required = False


class QuestionForm(ModelForm):

    class Meta:
        model = Question
        fields = ['questionID', 'user_id', 'courseID',
                  'subject', 'content', 'ddl', 'status', 'file']


class CourseForm(ModelForm):

    class Meta:
        model = Course
        fields = ['courseID', 'course', 'intro', 'teacher']
