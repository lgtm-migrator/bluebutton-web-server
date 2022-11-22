# Generated by Django 3.2.15 on 2022-11-17 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dot_ext", "0003_auto_20220422_2147"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="end_date",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="RESEARCH_STUDY End Date:"
            ),
        ),
        migrations.AddField(
            model_name="application",
            name="data_access_type",
            field=models.CharField(
                choices=[
                    ("ONE_TIME", "ONE_TIME - No refresh token needed."),
                    ("RESEARCH_STUDY", "RESEARCH_STUDY - Expires on end_date."),
                    ("THIRTEEN_MONTH", "THIRTEEN_MONTH - Access expires in 13-months."),
                ],
                default="ONE_TIME",
                max_length=16,
                null=True,
                verbose_name="Data Access Type:",
            ),
        ),
    ]
