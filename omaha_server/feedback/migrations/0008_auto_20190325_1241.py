# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-03-25 12:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0007_auto_20160608_1029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='email',
            field=models.CharField(blank=True, default=b'', max_length=500),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='page_url',
            field=models.CharField(blank=True, default=b'', max_length=2048),
        ),
    ]
