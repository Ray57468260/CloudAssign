from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .conf import settings
from .managers import UserInheritanceManager, UserManager


class AbstractUser(AbstractBaseUser, PermissionsMixin):
    USERS_AUTO_ACTIVATE = not settings.USERS_VERIFY_EMAIL

    email = models.EmailField(
        _('电子邮箱'), max_length=255, unique=True, db_index=True)
    is_staff = models.BooleanField(
        _('管理员'), default=False,
        help_text=_('Designates whether the user can log into this admin site.'))

    is_active = models.BooleanField(
        _('激活'), default=USERS_AUTO_ACTIVATE,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('注册时间'), default=timezone.now)
    user_type = models.ForeignKey(
        ContentType, null=True, editable=False, on_delete=models.CASCADE)

    objects = UserInheritanceManager()
    base_objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        abstract = True

    def get_full_name(self):
        """ Return the email."""
        return self.email

    def get_short_name(self):
        """ Return the email."""
        return self.email

    def email_user(self, subject, message, from_email=None):
        """ Send an email to this User."""
        send_mail(subject, message, from_email, [self.email])

    def activate(self):
        self.is_active = True
        self.save()

    def save(self, *args, **kwargs):
        if not self.user_type_id:
            self.user_type = ContentType.objects.get_for_model(
                self, for_concrete_model=False)
        super(AbstractUser, self).save(*args, **kwargs)


class User(AbstractUser):

    """
    Concrete class of AbstractUser.
    Use this if you don't need to extend User.
    """

    GENDER_CHOICES = (
        (u'M', u'男'),
        (u'F', u'女'),
    )

    user_id = models.CharField(_('学号'), max_length=255, primary_key=True, unique=True, help_text=_('Required. 10 characters. Digital only'),
                               error_messages={
        'unique': _("该学号已存在."),
    },)
    password = models.CharField(_('密码'), max_length=255)
    is_teacher = models.BooleanField(_('教师'), default=False)
    name = models.CharField(_('姓名'), max_length=25)
    gender = models.CharField(
        max_length=255, choices=GENDER_CHOICES, default='Female')
    dept = models.CharField(_('学院'), max_length=255)
    major = models.CharField(_('专业'), max_length=255)
    phonenumber = models.CharField(
        _('联系号码'), max_length=11, null=True)

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['email']

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
