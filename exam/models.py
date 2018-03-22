from django.db import models
from django.utils.translation import gettext_lazy as _
from dispatch.models import Course

# Create your models here.


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user_id, filename)


class BankProcess(models.Model):
    user_id = models.IntegerField(_('userID'), default=1)
    courseID = models.CharField(max_length=10)
    e_type = models.CharField(max_length=10)
    file = models.FileField(upload_to=user_directory_path, blank=True)


class Choice(models.Model):
    courseID = models.ForeignKey(
        Course, _('courseID'), related_name='Chioce_courseID')
    descri = models.TextField(_('题干'))
    is_single = models.BooleanField(
        _('是否单选'), default=True, help_text='若为多选题，请勿勾选')
    A = models.CharField(_('选项A'), max_length=255, blank=True)
    B = models.CharField(_('选项B'), max_length=255, blank=True)
    C = models.CharField(_('选项C'), max_length=255, blank=True)
    D = models.CharField(_('选项D'), max_length=255, blank=True)
    E = models.CharField(_('选项E'), max_length=255, blank=True)
    F = models.CharField(_('选项F'), max_length=255, blank=True)
    answer = models.CharField(_('答案'), max_length=4,
                              blank=True, help_text='参考形式：单选：A，多选：ABCD')
    point = models.IntegerField(_('分值'), default=0)
    created_at = models.DateTimeField(_('created_time'), auto_now_add=True)


class Judge(models.Model):
    courseID = models.ForeignKey(
        Course, _('courseID'), related_name='Judge_courseID')
    descri = models.TextField(_('题干'))
    answer = models.BooleanField(
        _('答案'), blank=True, help_text='勾选表示正确，不勾选表示错误')
    point = models.IntegerField(_('分值'), default=0)
    created_at = models.DateTimeField(_('created_time'), auto_now_add=True)


class S_answer(models.Model):
    courseID = models.ForeignKey(
        Course, _('courseID'), related_name='S_answer_courseID')
    descri = models.TextField(_('题干'))
    answer = models.TextField(_('答案'), blank=True)
    point = models.IntegerField(_('分值'), default=0)
    created_at = models.DateTimeField(_('created_time'), auto_now_add=True)


class Blank(models.Model):
    courseID = models.ForeignKey(
        Course, _('courseID'), related_name='Blank_courseID')
    descri = models.TextField(
        _('题干'), help_text='参考形式：我国交通事故报警求救电话号码是__[空1]__，以此类推')
    blank1 = models.CharField(_('空1'), max_length=255, blank=True)
    blank2 = models.CharField(_('空2'), max_length=255, blank=True)
    blank3 = models.CharField(_('空3'), max_length=255, blank=True)
    blank4 = models.CharField(_('空4'), max_length=255, blank=True)
    blank5 = models.CharField(_('空5'), max_length=255, blank=True)
    blank6 = models.CharField(_('空6'), max_length=255, blank=True)
    point = models.IntegerField(_('分值'), default=0)
    created_at = models.DateTimeField(_('created_time'), auto_now_add=True)


class Exam(models.Model):
    courseID = models.ForeignKey(
        Course, _('课程'), related_name='Exam_courseID')
    title = models.CharField(_('试卷题目'), max_length=64)
    intro = models.CharField(_('备注'), max_length=255, blank=True)
    choices = models.ManyToManyField(
        Choice, related_name='Exam_choices', blank=True)
    judges = models.ManyToManyField(
        Judge, related_name='Exam_judges', blank=True)
    s_answers = models.ManyToManyField(
        S_answer, related_name='Exam_s_answers', blank=True)
    blanks = models.ManyToManyField(
        Blank, related_name='Exam_blanks', blank=True)
    status = models.BooleanField(_('status'), default=True)
    created_at = models.DateTimeField(_('created_time'), auto_now_add=True)


class Draft(models.Model):
    courseID = models.ForeignKey(
        Course, _('课程'), related_name='Draft_courseID')
    title = models.CharField(_('试卷题目'), max_length=64, blank=True)
    intro = models.CharField(_('备注'), max_length=255, blank=True)
    draft_string = models.TextField(_('草稿'))
    status = models.BooleanField(_('status'), default=True)
    created_at = models.DateTimeField(_('created_time'), auto_now_add=True)
