# Generated by Django 4.2.16 on 2024-12-04 21:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0056_alter_event_end_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 4, 22, 29, 55, 468358, tzinfo=datetime.timezone.utc)),
        ),
    ]
