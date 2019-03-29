import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User

# Create your models here.

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Course(models.Model):
    courseID = models.IntegerField(
        _('课程'), primary_key=True, unique=True, default=000)
    course = models.CharField(_('课程名'), max_length=255)
    intro = models.TextField(_('introduction'))
    teacher = models.ForeignKey(
        User, _('teacher'), related_name='Course_teacher')
    student = models.ManyToManyField(
        User, related_name='Course_student')
    created_at = models.DateTimeField(_('created_time'), auto_now_add=True)

    class Meta:
        get_latest_by = 'created_at'

    def __str__(self):
        return '{0}'.format(self.course)


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user_id, filename)


class Question(models.Model):
    questionID = models.CharField(
        _('questionID'), max_length=255, primary_key=True, unique=True, default=000)
    user_id = models.IntegerField(_('userID'), default=1)
    courseID = models.ForeignKey(
        Course, related_name='Question_courseID', on_delete=models.SET_NULL, blank=True, null=True)
    subject = models.CharField(
        _('subject'), max_length=500, default='undefined')
    content = models.TextField(
        _('content'), default='Content')
    ddl = models.DateField(_('deadline'), max_length=255)
    status = models.BooleanField(
        _('status'), default=True, help_text='True to ongoing, False to closed')
    file = models.FileField(
        _('file'), upload_to=user_directory_path, blank=True)
    created_at = models.DateField(_('created_time'), auto_now_add=True)

    class Meta:
        get_latest_by = 'created_at'

    def __str__(self):
        return '{0}		{1}		{2}      {3}'.format(self.questionID, self.subject, self.courseID, self.created_at)


class Answer(models.Model):
    GRADE_CHOICES = (
        (0, '待评分'),
        (1, '驳回'),
        (55, 'C'),
        (65, 'B'),
        (75, 'A'),
        (85, 'A+'),
        (95, 'A++'),
    )  # 请与views.py的grade_map同步修改
    user_id = models.ForeignKey(
        User, related_name='Answer_owner', on_delete=models.CASCADE)
    questionID = models.ForeignKey(
        Question, related_name='Answer_questionID', on_delete=models.SET_NULL, blank=True, null=True)
    subject = models.CharField(
        _('subject'), max_length=500, default='undefined')
    content = models.TextField(
        _('content'), default='Content')
    accepted = models.BooleanField(
        _('accepted'), default=True, help_text='True to accepted, False to rejected')
    status = models.BooleanField(
        _('status'), default=True, help_text='True to active, False to closed')
    grade = models.IntegerField(choices=GRADE_CHOICES, default=0)
    suggestions = models.TextField(_('suggestions'), blank=True)
    file = models.FileField(
        _('file'), upload_to=user_directory_path, blank=True)
    created_at = models.DateTimeField(_('created_time'), auto_now_add=True)

    class Meta:
        get_latest_by = 'created_at'

    def __str__(self):
        return '{0}		{1}		{2}'.format(self.subject, self.status, self.created_at)
