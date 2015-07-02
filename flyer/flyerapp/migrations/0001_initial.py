# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('departure_date', models.DateTimeField(default=None, null=True)),
                ('landing_date', models.DateTimeField(default=None, null=True)),
                ('pub_date', models.DateTimeField(verbose_name=b'date published')),
                ('link', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=70)),
                ('iata_code', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('departure_date', models.DateTimeField(default=None, null=True)),
                ('landing_date', models.DateTimeField(default=None, null=True)),
                ('days_in_place', models.IntegerField()),
                ('departure_in_weekeng_only', models.BooleanField(default=False)),
                ('landing_in_weekeng_only', models.BooleanField(default=False)),
                ('pub_date', models.DateTimeField(verbose_name=b'date published')),
                ('departure', models.ForeignKey(related_name='departure_schedule', to='flyerapp.Place')),
                ('landing', models.ForeignKey(related_name='landing_schedule', to='flyerapp.Place')),
            ],
        ),
        migrations.AddField(
            model_name='flight',
            name='departure',
            field=models.ForeignKey(related_name='departure_flight', to='flyerapp.Place'),
        ),
        migrations.AddField(
            model_name='flight',
            name='landing',
            field=models.ForeignKey(related_name='landing_flight', to='flyerapp.Place'),
        ),
    ]
