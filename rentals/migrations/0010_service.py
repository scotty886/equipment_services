# Generated by Django 5.2 on 2025-04-25 23:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0009_rental_category_alter_rental_rental_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(default='item', max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('start_service_date', models.DateField()),
                ('end_service_date', models.DateField()),
                ('service_location', models.CharField(blank=True, max_length=100, null=True)),
                ('Resquestor', models.CharField(blank=True, max_length=100, null=True)),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('po_number', models.CharField(blank=True, max_length=100, null=True)),
                ('notes1', models.CharField(blank=True, max_length=300, null=True)),
                ('notes2', models.CharField(blank=True, max_length=300, null=True)),
                ('notes3', models.CharField(blank=True, max_length=300, null=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rentals.department')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rentals.vendor')),
            ],
        ),
    ]
