# Generated by Django 2.0.1 on 2018-03-16 09:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0017_auto_20180313_1351'),
    ]

    operations = [
        migrations.RenameField(
            model_name='draft',
            old_name='status',
            new_name='from_random',
        ),
    ]
