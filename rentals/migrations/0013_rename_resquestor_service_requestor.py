# Generated by Django 5.2 on 2025-04-26 01:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0012_remove_service_notes3'),
    ]

    operations = [
        migrations.RenameField(
            model_name='service',
            old_name='resquestor',
            new_name='requestor',
        ),
    ]
