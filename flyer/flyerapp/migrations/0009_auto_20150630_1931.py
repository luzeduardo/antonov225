# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('flyerapp', '0008_auto_20150630_1859'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='url_access',
        ),
        migrations.AddField(
            model_name='flight',
            name='schedule',
            field=models.ForeignKey(related_name='schedule_flight', default=None, to='flyerapp.Schedule'),
        ),
        migrations.AlterField(
            model_name='flight',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 30, 19, 31, 35, 119138), null=True, verbose_name=b'date published'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 30, 19, 31, 35, 117962), null=True, verbose_name=b'date published'),
        ),
    ]
