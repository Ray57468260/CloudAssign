# Generated by Django 2.0.3 on 2018-04-08 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('Male', '男'), ('Female', '女')], default='Female', max_length=255),
        ),
    ]
