# Generated by Django 5.2 on 2025-04-26 01:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0011_rename_resquestor_service_resquestor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='notes3',
        ),
    ]
