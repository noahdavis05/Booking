# Generated by Django 5.0.1 on 2024-07-02 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0012_restaurantfacility_friday_close_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='normalfacility',
            name='slot_quantity',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
