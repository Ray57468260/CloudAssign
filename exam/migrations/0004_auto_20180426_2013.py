# Generated by Django 2.0.1 on 2018-04-26 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0003_auto_20180426_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blank',
            name='sec',
            field=models.IntegerField(default=0, verbose_name='考点'),
        ),
        migrations.AlterField(
            model_name='choice',
            name='sec',
            field=models.IntegerField(default=0, verbose_name='考点'),
        ),
        migrations.AlterField(
            model_name='judge',
            name='sec',
            field=models.IntegerField(default=0, verbose_name='考点'),
        ),
        migrations.AlterField(
            model_name='s_answer',
            name='sec',
            field=models.IntegerField(default=0, verbose_name='考点'),
        ),
    ]
