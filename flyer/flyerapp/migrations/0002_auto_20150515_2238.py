# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flyerapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flight',
            name='departure_date',
            field=models.DateField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='flight',
            name='landing_date',
            field=models.DateField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='iata_code',
            field=models.CharField(max_length=3),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='departure_date',
            field=models.DateField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='landing_date',
            field=models.DateField(default=None, null=True),
        ),
    ]
