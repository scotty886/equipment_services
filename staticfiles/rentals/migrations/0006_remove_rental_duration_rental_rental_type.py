# Generated by Django 5.2 on 2025-04-21 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0005_vendor_coi_issued_vendor_agreement_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rental',
            name='duration',
        ),
        migrations.AddField(
            model_name='rental',
            name='rental_type',
            field=models.CharField(choices=[('ROS', 'ROS'), ('Drop Load', 'Drop Load')], default='ROS', max_length=100),
        ),
    ]
