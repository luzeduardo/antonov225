# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('flyerapp', '0007_auto_20150629_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='logic_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='flight',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 30, 18, 59, 57, 180047), null=True, verbose_name=b'date published'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 30, 18, 59, 57, 180807), null=True, verbose_name=b'date published'),
        ),
    ]
