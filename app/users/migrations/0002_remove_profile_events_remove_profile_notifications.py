# Generated by Django 4.2.16 on 2024-12-04 23:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='events',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='notifications',
        ),
    ]
