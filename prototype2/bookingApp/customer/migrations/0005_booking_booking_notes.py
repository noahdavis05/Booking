# Generated by Django 5.0.1 on 2024-07-07 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0004_restaurantbooking'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='booking_notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
