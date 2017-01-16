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
        json = ""
        i = 1
        for p in Poem.objects.all():
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

            xml += markup.to_xml().replace("\n", "\\n").replace('"', '\\"').replace("\t", "\\t").encode('utf-8').replace(b'<?xml version="1.0" encoding="UTF-8" ?>', b'')
            json += '{"model": "corpus.Markup", "fields": {' + \
                    '"text": "' + markup.to_xml().replace("\n", "\\n").replace('"', '\\"').replace("\t", "\\t") + '", ' + \
                    '"poem": ' + str(p.pk) + ', ' + \
                    '"author": "Automatic", ' + \
                    '"additional": "' + additional.replace("\n", "\\n").replace('"', '\\"').replace("\t", "\\t") + '"}},'
            i += 1
            if i % 100 == 0:
                print(i)
        json = "[" + json[:-1] + ']'
        with open(os.path.join(BASE_DIR, "datasets", "markup_django.json"), "w", encoding='utf-8') as f:
            f.write(json)
        with open(os.path.join(BASE_DIR, "datasets", "markup_dump.xml"), "wb") as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?><items>' + xml + b'</items>')