# Generated by Django 5.2 on 2025-05-01 22:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0004_vehicle_days'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='days',
        ),
    ]
