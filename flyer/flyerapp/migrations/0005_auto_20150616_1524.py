# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('flyerapp', '0004_auto_20150616_1040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flight',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 16, 15, 24, 34, 253091), null=True, verbose_name=b'date published'),
        ),
        migrations.AlterField(
            model_name='place',
            name='iata_code',
            field=models.CharField(unique=True, max_length=3),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 16, 15, 24, 34, 253789), null=True, verbose_name=b'date published'),
        ),
    ]
