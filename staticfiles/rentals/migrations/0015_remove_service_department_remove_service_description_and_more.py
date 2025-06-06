# Generated by Django 5.2 on 2025-04-26 01:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0014_productionservice'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='department',
        ),
        migrations.RemoveField(
            model_name='service',
            name='description',
        ),
        migrations.RemoveField(
            model_name='service',
            name='end_service_date',
        ),
        migrations.RemoveField(
            model_name='service',
            name='notes1',
        ),
        migrations.RemoveField(
            model_name='service',
            name='notes2',
        ),
        migrations.RemoveField(
            model_name='service',
            name='po_number',
        ),
        migrations.RemoveField(
            model_name='service',
            name='requestor',
        ),
        migrations.RemoveField(
            model_name='service',
            name='service_location',
        ),
        migrations.RemoveField(
            model_name='service',
            name='start_service_date',
        ),
        migrations.RemoveField(
            model_name='service',
            name='title',
        ),
        migrations.RemoveField(
            model_name='service',
            name='vendor',
        ),
        migrations.DeleteModel(
            name='ProductionService',
        ),
    ]
