# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Генерация, загрузка и сохранение разметок по текстам.

from django.core.management.base import BaseCommand
import os

from poetry.settings import BASE_DIR
from poetry.apps.corpus.models import Poem, MarkupInstance as ModelMarkup
from rupo.accents.classifier import MLAccentClassifier
from rupo.accents.dict import AccentDict
from rupo.main.phonetics import Phonetics
from rupo.metre.metre_classifier import MetreClassifier
from rupo.files.writer import Writer, FileTypeEnum


class Command(BaseCommand):
    help = 'Automatic markup dump'

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
        parser.add_argument('--xml',
                            action='store',
                            dest='xml',
                            default=None,
                            help='XML path')
        parser.add_argument('--raw',
                            action='store',
                            dest='raw',
                            default=None,
                            help='Plain text markup path')
        parser.add_argument('--db',
                            action='store_true',
                            dest='db',
                            default=False,
                            help='Save to db?')

    def handle(self, *args, **options):
        accents_dict = AccentDict()
        accents_classifier = MLAccentClassifier(accents_dict)

        poems = Poem.objects.all()
        begin = int(options.get('from'))
        end = int(options.get('to')) if options.get('to') is not None else len(poems)
        poems = Poem.objects.all()[begin:end]

        xml_path = str(options.get('xml')) if options.get('xml') is not None else None
        raw_path = str(options.get('raw')) if options.get('raw') is not None else None

        db = options.get('db')

        xml_writer = None
        raw_writer = None
        if xml_path is not None:
            xml_path = os.path.join(BASE_DIR, xml_path)
            xml_writer = Writer(FileTypeEnum.XML, xml_path)
            xml_writer.open()
        if raw_path is not None:
            raw_path = os.path.join(BASE_DIR, raw_path)
            raw_writer = Writer(FileTypeEnum.RAW, raw_path)
            raw_writer.open()
        i = 0
        for p in poems:
            markup = Phonetics.process_text(p.text, accents_dict)
            markup, result = MetreClassifier.improve_markup(markup, accents_classifier)
            if xml_writer is not None:
                xml_writer.write_markup(markup)
            if raw_writer is not None:
                raw_writer.write_markup(markup)
            if db:
                ModelMarkup.objects.create(poem=p, text=markup.to_json(),
                                           author="Automatic", additional=result.to_json())
            i += 1
            print(i)
        if raw_writer is not None:
            raw_writer.close()
        if xml_writer is not None:
            xml_writer.close()