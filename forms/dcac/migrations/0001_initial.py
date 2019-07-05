# Generated by Django 2.0.6 on 2019-07-05 14:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicYear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='ACGReimbursementForm',
            fields=[
                ('form_id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('name_on_account', models.CharField(max_length=100)),
                ('account_number', models.CharField(max_length=20)),
                ('sort_code', models.CharField(max_length=20)),
                ('jcr_treasurer_approved', models.BooleanField(default=False)),
                ('jcr_treasurer_comments', models.CharField(max_length=500)),
                ('senior_treasurer_approved', models.BooleanField(default=False)),
                ('senior_treasurer_comments', models.CharField(max_length=500)),
                ('bursary_paid', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ACGReimbursementFormItemEntry',
            fields=[
                ('entry_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=500)),
                ('form', models.ForeignKey(default=None, on_delete=django.db.models.deletion.SET_DEFAULT, to='dcac.ACGReimbursementForm')),
            ],
        ),
        migrations.CreateModel(
            name='ACGReimbursementFormReceiptEntry',
            fields=[
                ('entry_id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='BudgetEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('organization_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('user_id', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='CRSid')),
                ('first_name', models.CharField(max_length=50, verbose_name='First Name')),
                ('surname', models.CharField(max_length=50, verbose_name='Surname')),
            ],
        ),
        migrations.AddField(
            model_name='organization',
            name='president',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.SET_DEFAULT, to='dcac.Student'),
        ),
        migrations.AddField(
            model_name='budgetentry',
            name='organization',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.SET_DEFAULT, to='dcac.Organization'),
        ),
        migrations.AddField(
            model_name='budgetentry',
            name='year',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.SET_DEFAULT, to='dcac.AcademicYear'),
        ),
        migrations.AddField(
            model_name='acgreimbursementform',
            name='organization',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.SET_DEFAULT, to='dcac.Organization'),
        ),
        migrations.AddField(
            model_name='acgreimbursementform',
            name='year',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.SET_DEFAULT, to='dcac.AcademicYear'),
        ),
    ]
