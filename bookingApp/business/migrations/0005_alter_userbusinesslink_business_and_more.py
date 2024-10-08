# Generated by Django 5.0.6 on 2024-06-06 22:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0004_userbusinesslink'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbusinesslink',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='business.business'),
        ),
        migrations.AlterField(
            model_name='userbusinesslink',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='business_link', to=settings.AUTH_USER_MODEL),
        ),
    ]
