# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('flyerapp', '0003_auto_20150615_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flight',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 16, 10, 40, 26, 512493), null=True, verbose_name=b'date published'),
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='landing',
        ),
        migrations.AddField(
            model_name='schedule',
            name='landing',
            field=models.ManyToManyField(related_name='landing_schedule', to='flyerapp.Place'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 16, 10, 40, 26, 513225), null=True, verbose_name=b'date published'),
        ),
    ]
