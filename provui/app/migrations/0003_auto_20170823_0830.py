# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-23 08:30
from __future__ import unicode_literals

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_delete_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='idd_data',
            name='customer',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='idd_data',
            name='zone',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='docfile',
            field=models.FileField(upload_to=app.models.generate_filename),
        ),
    ]
