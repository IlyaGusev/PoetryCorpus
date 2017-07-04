# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-03 14:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0005_auto_20170703_1702'),
    ]

    operations = [
        migrations.CreateModel(
            name='Markup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Имя разметки')),
                ('additional', models.TextField(blank=True, verbose_name='Дополнительная ифнормация')),
            ],
            options={
                'verbose_name': 'Разметка',
                'verbose_name_plural': 'Разметки',
            },
        ),
        migrations.RenameModel(
            old_name='MarkupVersion',
            new_name='MarkupInstance',
        ),
        migrations.AlterModelOptions(
            name='markupinstance',
            options={'verbose_name': 'Экзепляр разметки', 'verbose_name_plural': 'Экзепляры разметки'},
        ),
    ]
