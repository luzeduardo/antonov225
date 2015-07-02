# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('flyerapp', '0005_auto_20150616_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='flight',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 16, 16, 28, 54, 628011), null=True, verbose_name=b'date published'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 16, 16, 28, 54, 628731), null=True, verbose_name=b'date published'),
        ),
    ]
