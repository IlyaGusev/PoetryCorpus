# -*- coding: utf-8 -*-
import os
import sys

from django.core.management.base import BaseCommand

from poetry.apps.corpus.models import Poem
from poetry.apps.corpus.scripts.accents.classifier import MLAccentClassifier
from poetry.apps.corpus.scripts.accents.dict import AccentDict
from poetry.apps.corpus.scripts.main.phonetics import Phonetics
from poetry.apps.corpus.scripts.metre.metre_classifier import MetreClassifier
from poetry.settings import BASE_DIR


class Command(BaseCommand):
    help = 'Automatic markup update'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('--from',
                            action='store',
                            dest='from',
                            default=0,
                            help='Begin')
        parser.add_argument('--to',
                            action='store',
                            dest='to',
                            default=None,
                            help='End')

        parser.add_argument('--mode',
                            action='store',
                            dest='mode',
                            default=0,
                            help='Mode')

    def handle(self, *args, **options):
        poems = Poem.objects.all()
        mode = int(options.get('mode'))
        begin = int(options.get('from'))
        end = int(options.get('to')) if options.get('to') is not None else len(poems)
        poems = Poem.objects.all()[begin:end]
        accents_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict"))
        accents_classifier = MLAccentClassifier(os.path.join(BASE_DIR, "datasets", "models"), accents_dict)
        i = 1
        with open(os.path.join(BASE_DIR, "datasets", "corpus", "markup_dump.xml"), "wb") as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?><items>')
            for p in poems:
                if mode == 0:
                    markup = Phonetics.process_text(p.text, accents_dict)
                    markup, result = MetreClassifier.improve_markup(markup, accents_classifier)
                else:
                    markup = p.markups.all()[0].get_markup()
                xml = markup.to_xml().encode('utf-8').replace(b'<?xml version="1.0" encoding="UTF-8" ?>', b'')\
                    .decode('utf-8').replace("\n", "\\n").replace('"', '\\"').replace("\t", "\\t").encode('utf-8')
                f.write(xml)
                i += 1
                sys.stdout.write(str(i)+"\n")
                sys.stdout.flush()
            f.write(b'</items>')
