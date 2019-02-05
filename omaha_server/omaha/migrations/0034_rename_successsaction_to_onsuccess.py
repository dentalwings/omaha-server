# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import omaha.fields


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0033_auto_20171020_0919'),
    ]

    operations = [
        migrations.RenameField('Action', 'successsaction', 'onsuccess'),
    ]
