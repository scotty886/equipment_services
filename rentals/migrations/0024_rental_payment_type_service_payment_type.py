# Generated by Django 5.2 on 2025-04-26 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0023_service_production_service_service_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='rental',
            name='payment_type',
            field=models.CharField(choices=[('net30', 'Net30'), ('check', 'Check'), ('credit_card', 'Credit Card'), ('cash', 'Cash')], default='choose payment type', max_length=100),
        ),
        migrations.AddField(
            model_name='service',
            name='payment_type',
            field=models.CharField(choices=[('net30', 'Net30'), ('check', 'Check'), ('credit_card', 'Credit Card'), ('cash', 'Cash')], default='choose payment type', max_length=100),
        ),
    ]
