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
    help = 'Automatic markup dump for Django'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('--count',
                            action='store',
                            dest='count',
                            default=None,
                            help='Number of elems')

    def handle(self, *args, **options):
        accents_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict.txt"))
        accents_classifier = AccentClassifier(os.path.join(BASE_DIR, "datasets", "models"), accents_dict)
        json = ""
        i = 1

        poems = Poem.objects.all() if options.get('count') is None else Poem.objects.all()[:int(options.get('count'))]
        for p in poems:
            markup = Phonetics.process_text(p.text, accents_dict)
            classifier = MetreClassifier(markup, accents_classifier)
            metre = classifier.classify_metre()
            classifier.get_ml_results()
            markup = classifier.get_improved_markup()
            rhymes = Phonetics.get_all_rhymes(markup, {}, 4)

            additional = list()
            lines = []
            for word1, pair in rhymes.items():
                line = [word1]
                for word2, freq in pair.items():
                    line.append(word2)
                lines.append(" - ".join(line))
            additional.append("Метр: " + str(metre))
            additional.append("Снятая омография: \n" +
                              "\n".join([str((item['word_text'], item['syllable_number']))
                                         for item in classifier.omograph_resolutions[metre]]))
            additional.append("Неправильные ударения: \n" +
                              "\n".join([str((item['word_text'], item['syllable_number']))
                                         for item in classifier.corrected_accents[metre]]))
            additional.append("Новые ударения: \n" +
                              "\n".join([str((item['word_text'], item['syllable_number']))
                                         for item in classifier.additions[metre]]))
            additional.append("ML: \n" +
                              "\n".join([str((item['word_text'], item['syllable_number']))
                                         for item in classifier.after_ml]))
            additional.append("Рифмы: \n" + "\n".join(lines))
            additional = "\n".join(additional)
            text = markup.to_xml().replace("\n", "\\n").replace('"', '\\"').replace("\t", "\\t")
            additional = additional.replace("\n", "\\n").replace('"', '\\"').replace("\t", "\\t")

            json += '{"model": "corpus.Markup", "fields": {' + \
                    '"text": "' + text + '", ' + \
                    '"poem": ' + str(p.pk) + ', ' + \
                    '"author": "Automatic", ' + \
                    '"additional": "' + additional + '"}},'
            i += 1
            if i % 100 == 0:
                print(i)
        json = "[" + json[:-1] + ']'
        with open(os.path.join(BASE_DIR, "datasets", "django", "markup_django.json"), "w", encoding='utf-8') as f:
            f.write(json)