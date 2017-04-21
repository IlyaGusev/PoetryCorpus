
# -*- coding: utf-8 -*-
import os

from django.core.management.base import BaseCommand
from poetry.apps.corpus.models import Poem

class Command(BaseCommand):
    help = 'Automatic markup dump for Django'

    def add_arguments(self, parser):
        parser.add_argument('--out',
                            action='store',
                            dest='out',
                            default="",
                            help='Output')

    def handle(self, *args, **options):
        output = options.get('out')
        with open(output, "w", encoding='utf-8') as f:
            content = '['
            poems = [poem for poem in Poem.objects.all() if poem.count_manual_markups() != 0]
            markups = []
            for poem in poems:
                for markup in poem.markups.all():
                    if markup.author != "Automatic":
                        markups.append(markup)
                        break
            print(len(markups))
            for markup in markups:
                content += markup.text + ","
            content = content[:-1] + ']'
            f.write(content)