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
    help = 'Dict update by classification'

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
        parser.add_argument('--border',
                            action='store',
                            dest='border',
                            default=1,
                            help='Error border')

    def handle(self, *args, **options):
        accents_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict"))
        accents_classifier = MLAccentClassifier(os.path.join(BASE_DIR, "datasets", "models"), accents_dict)
        poems = Poem.objects.all()
        begin = int(options.get('from'))
        end = int(options.get('to')) if options.get('to') is not None else len(poems)
        border = int(options.get('border'))

        i = 0
        poems = Poem.objects.all()[begin:end]
        for p in poems:
            markup = Phonetics.process_text(p.text, accents_dict)
            markup, result = MetreClassifier.improve_markup(markup, accents_classifier)
            if result.metre in ["iambos", "choreios", "daktylos", "amphibrachys", "anapaistos"]:
                if result.get_metre_errors_count() <= border:
                    for addition in result.additions[result.metre]:
                        accents_dict.update(addition['word_text'].lower(), {addition['accent'], })
                    for correction in result.corrections[result.metre]:
                        accents_dict.update(correction['word_text'].lower(), {correction['accent'], })
            i += 1
            if i % 100 == 0:
                print(i)
        accents_dict.save(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict_modified"))

