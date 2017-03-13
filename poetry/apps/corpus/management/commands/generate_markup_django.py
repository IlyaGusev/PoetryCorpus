# -*- coding: utf-8 -*-
import os

from django.core.management.base import BaseCommand

from poetry.apps.corpus.models import Poem
from poetry.apps.corpus.scripts.accents.classifier import MLAccentClassifier
from poetry.apps.corpus.scripts.accents.dict import AccentDict
from poetry.apps.corpus.scripts.main.phonetics import Phonetics
from poetry.apps.corpus.scripts.metre.metre_classifier import MetreClassifier
from poetry.settings import BASE_DIR


class Command(BaseCommand):
    help = 'Automatic markup dump for Django'

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

    def handle(self, *args, **options):
        accents_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict"))
        accents_classifier = MLAccentClassifier(os.path.join(BASE_DIR, "datasets", "models"), accents_dict)
        i = 1
        poems = Poem.objects.all()
        begin = int(options.get('from'))
        end = int(options.get('to')) if options.get('to') is not None else len(poems)
        poems = Poem.objects.all()[begin:end]

        filename = os.path.join(BASE_DIR, "datasets", "django", "markup_django.json")
        try:
            os.remove(filename)
        except OSError:
            pass
        with open(filename, "a+", encoding='utf-8') as f:
            f.write("[")
            for p in poems:
                markup = Phonetics.process_text(p.text, accents_dict)
                markup, result = MetreClassifier.improve_markup(markup, accents_classifier)
                text = markup.to_json().replace("\n", "\\n").replace('\\', '\\\\').replace('"', '\\"').replace("\t", "\\t")
                additional = result.to_json().replace("\n", "\\n").replace('\\', '\\\\').replace('"', '\\"').replace("\t", "\\t")

                json = '{"model": "corpus.Markup", "fields": {' + \
                        '"text": "' + text + '", ' + \
                        '"poem": ' + str(p.pk) + ', ' + \
                        '"author": "Automatic", ' + \
                        '"additional": "' + additional + '"}},'
                f.write(json)
                i += 1
                print(i)
            f.seek(0, 2)
            size = f.tell()
            f.truncate(size - 1)
            f.write(']')
