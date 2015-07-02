# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('flyerapp', '0006_auto_20150616_1628'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='price_percent_highter',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='price_percent_lower',
        ),
        migrations.AddField(
            model_name='schedule',
            name='price_highter',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='schedule',
            name='price_lower',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='flight',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 29, 11, 35, 23, 867220), null=True, verbose_name=b'date published'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 29, 11, 35, 23, 867961), null=True, verbose_name=b'date published'),
        ),
    ]
