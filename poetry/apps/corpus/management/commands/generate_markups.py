# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Генерация, загрузка и сохранение разметок по текстам.

from django.core.management.base import BaseCommand

from poetry.apps.corpus.models import Poem, Markup as ModelMarkup
from rupo.accents.classifier import MLAccentClassifier
from rupo.accents.dict import AccentDict
from rupo.main.phonetics import Phonetics
from rupo.metre.metre_classifier import MetreClassifier
from rupo.files.writer import Writer, FileTypeEnum
from poetry.apps.corpus.scripts.settings import MARKUPS_DUMP_XML_PATH, MARKUPS_DUMP_RAW_PATH


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
        accents_dict = AccentDict()
        accents_classifier = MLAccentClassifier(accents_dict)

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
            markup, result = MetreClassifier.improve_markup(markup, accents_classifier)
            xml_writer.write_markup(markup)
            raw_writer.write_markup(markup)
            ModelMarkup.objects.create(poem=p, text=markup.to_json(),
                                       author="Automatic", additional=result.to_json())
            i += 1
            print(i)
        raw_writer.close()
        xml_writer.close()