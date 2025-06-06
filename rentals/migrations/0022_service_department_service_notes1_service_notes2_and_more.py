# Generated by Django 5.2 on 2025-04-26 16:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0021_service_vendor'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rentals.department'),
        ),
        migrations.AddField(
            model_name='service',
            name='notes1',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='service',
            name='notes2',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='service',
            name='purchase_order',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='service',
            name='title',
            field=models.CharField(blank=True, default='title', max_length=100, null=True),
        ),
    ]
