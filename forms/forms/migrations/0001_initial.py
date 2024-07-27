# Generated by Django 2.2.28 on 2024-07-24 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminUser',
            fields=[
                ('user_id', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='CRSid')),
                ('first_name', models.CharField(max_length=50, verbose_name='First Name')),
                ('surname', models.CharField(max_length=50, verbose_name='Surname')),
                ('role', models.IntegerField(choices=[(1, 'JCR Treasurer'), (2, 'Senior Treasurer'), (3, 'Bursary'), (4, 'Assistant Bursar')], verbose_name='Role')),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('organization_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=500)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('user_id', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='CRSid')),
                ('first_name', models.CharField(max_length=50, verbose_name='First Name')),
                ('surname', models.CharField(max_length=50, verbose_name='Surname')),
            ],
        ),
    ]
