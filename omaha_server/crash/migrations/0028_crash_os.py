# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-04-14 10:54


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0027_auto_20170304_0619'),
    ]

    operations = [
        migrations.AddField(
            model_name='crash',
            name='os',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
