# Generated by Django 4.2.16 on 2024-12-05 19:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0062_alter_event_attendee_alter_event_end_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 5, 20, 50, 3, 719508, tzinfo=datetime.timezone.utc)),
        ),
    ]
