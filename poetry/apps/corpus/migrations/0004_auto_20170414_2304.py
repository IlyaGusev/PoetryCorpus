# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0003_generationsettings_line'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='poem',
            options={'verbose_name': 'Стихотворение', 'verbose_name_plural': 'Стихотворения', 'permissions': (('can_view_restricted_poems', 'Can view restricted poems'),)},
        ),
        migrations.AddField(
            model_name='poem',
            name='is_restricted',
            field=models.BooleanField(verbose_name='Стихи с ограниченным доступом', default=False),
        ),
    ]
