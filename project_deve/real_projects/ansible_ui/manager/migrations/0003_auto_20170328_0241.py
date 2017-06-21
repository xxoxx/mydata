# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-28 02:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_auto_20170328_0234'),
    ]

    operations = [
        migrations.AddField(
            model_name='hosts',
            name='service_start_path',
            field=models.CharField(default='/home/tomcat/tomcat-7.0.54/bin/start.sh', max_length=80),
        ),
        migrations.AddField(
            model_name='hosts',
            name='service_stop_path',
            field=models.CharField(default='/home/tomcat/tomcat7.0.54/bin/stop.sh', max_length=80),
        ),
        migrations.AddField(
            model_name='hosts',
            name='svn_path',
            field=models.CharField(default='', max_length=100),
        ),
    ]
