# Generated by Django 3.2.13 on 2022-04-22 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0002_auto_20210903_0030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forms',
            name='form_data',
            field=models.JSONField(),
        ),
    ]
