# Generated by Django 4.2.16 on 2024-11-17 06:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0030_alter_event_end_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 17, 7, 19, 11, 863131, tzinfo=datetime.timezone.utc)),
        ),
    ]
