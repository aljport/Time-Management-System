# Generated by Django 4.2.17 on 2024-12-06 05:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0067_alter_event_end_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 6, 6, 11, 30, 663535, tzinfo=datetime.timezone.utc)),
        ),
    ]
