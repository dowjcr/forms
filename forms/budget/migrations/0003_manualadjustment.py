# Generated by Django 2.2.28 on 2024-08-09 21:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0002_auto_20240724_1133'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManualAdjustment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('reason', models.TextField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('fund_source', models.IntegerField(choices=[(1, 'Annual Consumable Grant'), (2, 'Depreciation Fund')], default=1)),
                ('date', models.DateField()),
                ('added_by', models.CharField(max_length=8)),
                ('budget', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='budget.Budget')),
            ],
        ),
    ]
