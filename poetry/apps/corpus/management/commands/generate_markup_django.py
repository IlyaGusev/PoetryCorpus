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
        accents_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict.txt"))
        accents_classifier = AccentClassifier(os.path.join(BASE_DIR, "datasets", "models"), accents_dict)
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

                json = '{"model": "corpus.Markup", "fields": {' + \
                        '"text": "' + text + '", ' + \
                        '"poem": ' + str(p.pk) + ', ' + \
                        '"author": "Automatic", ' + \
                        '"additional": "' + additional + '"}},'
                f.write(json)
                i += 1
                if i % 100 == 0:
                    print(i)
            f.seek(0, 2)
            size = f.tell()
            f.truncate(size - 1)
            f.write(']')
