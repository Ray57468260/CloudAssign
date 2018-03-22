from __future__ import unicode_literals

from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user_id, filename)


class FileSimpleModel(models.Model):
    """
    文件接收 Model
    upload_to：表示文件保存位置
    """
    user_id = models.CharField(_('userID'), max_length=255)
    file_name = models.CharField(_('filename'), max_length=255)
    file = models.FileField(
        _('filepath'), upload_to=user_directory_path)
    tiemstamp = models.DateTimeField(_('created_time'), auto_now_add=True)
    note = models.TextField(_('note'), max_length=255)

    class meta:
        verbose_name = _('FileSimpleModel')
        verbose_name_plural = _('FileSimpleModels')

    def __str__(self):
        return self.file_name
