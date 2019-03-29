from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Exam)
admin.site.register(Choice)
admin.site.register(Blank)
admin.site.register(Judge)
admin.site.register(S_answer)
admin.site.register(Draft)
