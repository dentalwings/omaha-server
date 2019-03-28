# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from omaha.fields import BigVersionField


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0007_auto_20141113_0906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='version',
            name='version',
            field=BigVersionField(help_text=b'Format: 255.255.65535.65535', db_index=True),
            preserve_default=True,
        ),
    ]
