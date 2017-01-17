# -*- coding: utf-8 -*-
import os

from django.core.management.base import BaseCommand
from poetry.settings import BASE_DIR
from poetry.apps.corpus.scripts.phonetics.accent_classifier import AccentClassifier
from poetry.apps.corpus.scripts.phonetics.accent_dict import AccentDict
from poetry.apps.corpus.scripts.metre.metre_classifier import MetreClassifier
from poetry.apps.corpus.models import Poem, Markup
from poetry.apps.corpus.scripts.phonetics.phonetics import Phonetics


class Command(BaseCommand):
    help = 'Automatic markup update'

    def handle(self, *args, **options):
        accents_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict.txt"))
        accents_classifier = AccentClassifier(os.path.join(BASE_DIR, "datasets", "models"), accents_dict)
        xml = b""
        i = 1
        for p in Poem.objects.all():
            markup = Phonetics.process_text(p.text, accents_dict)
            classifier = MetreClassifier(markup, accents_classifier)
            classifier.classify_metre()
            classifier.get_ml_results()
            markup = classifier.get_improved_markup()
            xml += markup.to_xml().encode('utf-8').replace(b'<?xml version="1.0" encoding="UTF-8" ?>', b'')\
                .decode('utf-8').replace("\n", "\\n").replace('"', '\\"').replace("\t", "\\t").encode('utf-8')

            i += 1
            if i % 100 == 0:
                print(i)
        with open(os.path.join(BASE_DIR, "datasets", "markup_dump.xml"), "wb") as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?><items>' + xml + b'</items>')