# Generated by Django 5.2 on 2025-04-20 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0003_rename_contact_vendor_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='services',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
