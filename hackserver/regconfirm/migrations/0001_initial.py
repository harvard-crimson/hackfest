# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Registrant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=50, blank=True)),
                ('email', models.CharField(default=b'', unique=True, max_length=100, db_index=True)),
                ('confirmed', models.BooleanField(default=False)),
                ('secret', models.CharField(default=b'', max_length=32)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
