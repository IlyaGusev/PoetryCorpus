# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Генерация, загрузка и сохранение разметок по текстам.

from django.core.management.base import BaseCommand

from poetry.apps.corpus.models import Poem, Markup as ModelMarkup
from poetry.apps.corpus.scripts.accents.classifier import MLAccentClassifier
from poetry.apps.corpus.scripts.accents.dict import AccentDict
from poetry.apps.corpus.scripts.main.phonetics import Phonetics
from poetry.apps.corpus.scripts.metre.metre_classifier import MetreClassifier
from poetry.apps.corpus.scripts.settings import DICT_PATH, CLASSIFIER_PATH, MARKUPS_DUMP_XML_PATH, MARKUPS_DUMP_RAW_PATH
from poetry.apps.corpus.scripts.convertion.writer import Writer, FileTypeEnum


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
        accents_dict = AccentDict(DICT_PATH)
        accents_classifier = MLAccentClassifier(CLASSIFIER_PATH, accents_dict)

        poems = Poem.objects.all()
        begin = int(options.get('from'))
        end = int(options.get('to')) if options.get('to') is not None else len(poems)
        poems = Poem.objects.all()[begin:end]

        xml_writer = Writer(FileTypeEnum.XML, MARKUPS_DUMP_XML_PATH)
        xml_writer.open()
        raw_writer = Writer(FileTypeEnum.RAW, MARKUPS_DUMP_RAW_PATH)
        raw_writer.open()
        i = 0
        for p in poems:
            markup = Phonetics.process_text(p.text, accents_dict)
            markup, result = MetreClassifier.improve_markup(markup) #accents_classifier)
            xml_writer.write_markup(markup)
            raw_writer.write_markup(markup)
            ModelMarkup.objects.create(poem=p, text=markup.to_json(),
                                       author="Automatic", additional=result.to_json())
            i += 1
            print(i)
        raw_writer.close()
        xml_writer.close()