# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0034_auto_20190409_0431'),
    ]

    operations = [
        migrations.RenameField('Action', 'successsaction', 'onsuccess'),
    ]
