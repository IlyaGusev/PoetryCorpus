# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Генерация, загрузка и сохранение разметок по текстам.

from django.core.management.base import BaseCommand
import os

from poetry.settings import BASE_DIR
from poetry.apps.corpus.models import Poem, Markup as ModelMarkup, MarkupVersion
from rupo.metre.metre_classifier import MetreClassifier
from rupo.files.writer import Writer, FileType
from rupo.main.markup import Markup
from rupo.api import Engine

STRESS_MODEL = "./data/stress_models/stress_ru_LSTM64_dropout0.2_acc99_wer8.h5"
ZALYZNYAK_DICT = "./data/dict/zaliznyak.txt"
TRIE_PATH = "./data/dict/stress.trie"
RAW_DICT_PATH = "./data/dict/stress_raw_dict.txt"


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
        parser.add_argument('--author',
                            action='store',
                            dest='author',
                            default="AutomaticV2",
                            help='Author')

    def handle(self, *args, **options):
        engine = Engine(language="ru")
        poems = Poem.objects.all()
        begin = int(options.get('from'))
        end = int(options.get('to')) if options.get('to') is not None else len(poems)
        poems = Poem.objects.all()[begin:end]

        xml_path = str(options.get('xml')) if options.get('xml') is not None else None
        raw_path = str(options.get('raw')) if options.get('raw') is not None else None

        db = options.get('db')
        author = options.get("author")
        markup_version = MarkupVersion.objects.get_or_create(name=author)[0]
        ModelMarkup.objects.filter(markup_version=markup_version).delete()

        xml_writer = None
        raw_writer = None
        if xml_path is not None:
            xml_path = os.path.join(BASE_DIR, xml_path)
            xml_writer = Writer(FileType.XML, xml_path)
            xml_writer.open()
        if raw_path is not None:
            raw_path = os.path.join(BASE_DIR, raw_path)
            raw_writer = Writer(FileType.RAW, raw_path)
            raw_writer.open()
        i = 0
        stress_predictor = engine.get_stress_predictor(stress_model_path=STRESS_MODEL, zalyzniak_dict=ZALYZNYAK_DICT,
                                                       stress_trie_path=TRIE_PATH, raw_stress_dict_path=RAW_DICT_PATH)
        for p in poems:
            if "Automatic" in author:
                markup = Markup.process_text(p.text, stress_predictor)
                markup, result = MetreClassifier.improve_markup(markup)
                if xml_writer is not None:
                    xml_writer.write_markup(markup)
                if raw_writer is not None:
                    raw_writer.write_markup(markup)
                if db:
                    ModelMarkup.objects.create(poem=p, text=markup.to_json(),
                                               author="Automatic2", additional=result.to_json(),
                                               markup_version=markup_version)
            else:
                markup = p.markups.filter(author=author)[0]
                if xml_writer is not None:
                    xml_writer.write_markup(markup.get_markup())
                if raw_writer is not None:
                    raw_writer.write_markup(markup.get_markup())
            i += 1
            print(i)
        if raw_writer is not None:
            raw_writer.close()
        if xml_writer is not None:
            xml_writer.close()