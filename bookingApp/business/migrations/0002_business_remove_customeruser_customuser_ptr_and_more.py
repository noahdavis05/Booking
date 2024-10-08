# Generated by Django 5.0.6 on 2024-06-06 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('business_id', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField()),
                ('password', models.CharField(max_length=128)),
            ],
        ),
        migrations.RemoveField(
            model_name='customeruser',
            name='customuser_ptr',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='user_permissions',
        ),
        migrations.DeleteModel(
            name='BusinessUser',
        ),
        migrations.DeleteModel(
            name='CustomerUser',
        ),
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]
