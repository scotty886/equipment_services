# Generated by Django 5.2 on 2025-04-26 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0016_service_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
