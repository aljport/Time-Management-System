# Generated by Django 4.2.16 on 2024-11-21 22:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0042_alter_event_end_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 21, 23, 14, 23, 66924, tzinfo=datetime.timezone.utc)),
        ),
    ]