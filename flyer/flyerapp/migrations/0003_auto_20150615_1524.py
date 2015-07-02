# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('flyerapp', '0002_auto_20150515_2238'),
    ]

    operations = [
        migrations.CreateModel(
            name='PossibleFlights',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pub_date', models.DateTimeField(verbose_name=b'date published')),
            ],
        ),
        migrations.RenameField(
            model_name='schedule',
            old_name='departure_in_weekeng_only',
            new_name='departure_in_weekend_only',
        ),
        migrations.RenameField(
            model_name='schedule',
            old_name='landing_in_weekeng_only',
            new_name='exactly_days_check',
        ),
        migrations.AddField(
            model_name='schedule',
            name='email',
            field=models.CharField(default=None, max_length=80, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='landing_in_weekend_only',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='schedule',
            name='price_percent_highter',
            field=models.DecimalField(default=1.3, max_digits=2, decimal_places=1),
        ),
        migrations.AddField(
            model_name='schedule',
            name='price_percent_lower',
            field=models.DecimalField(default=1.3, max_digits=2, decimal_places=1),
        ),
        migrations.AddField(
            model_name='schedule',
            name='url_access',
            field=models.TextField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='flight',
            name='departure_date',
            field=models.DateField(default=None),
        ),
        migrations.AlterField(
            model_name='flight',
            name='landing_date',
            field=models.DateField(default=None),
        ),
        migrations.AlterField(
            model_name='flight',
            name='pub_date',
            field=models.DateTimeField(null=True, verbose_name=b'date published'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='departure_date',
            field=models.DateField(default=None),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='landing_date',
            field=models.DateField(default=None),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 15, 15, 24, 17, 235408), null=True, verbose_name=b'date published'),
        ),
        migrations.AddField(
            model_name='possibleflights',
            name='schedule',
            field=models.ForeignKey(related_name='schedule_schedule', to='flyerapp.Schedule'),
        ),
    ]
