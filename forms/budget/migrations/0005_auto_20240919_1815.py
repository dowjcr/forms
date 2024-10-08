# Generated by Django 2.2.28 on 2024-09-19 18:15

import budget.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0004_auto_20240919_1618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='president',
            field=models.CharField(max_length=100, verbose_name='President(s)'),
        ),
        migrations.AlterField(
            model_name='budget',
            name='president_crsid',
            field=budget.models.MultiCRSidField(max_length=30, verbose_name='CRSid(s)'),
        ),
        migrations.AlterField(
            model_name='budget',
            name='treasurer',
            field=models.CharField(max_length=100, verbose_name='Treasurer(s)'),
        ),
        migrations.AlterField(
            model_name='budget',
            name='treasurer_crsid',
            field=budget.models.MultiCRSidField(max_length=30, verbose_name='CRSid(s)'),
        ),
    ]
