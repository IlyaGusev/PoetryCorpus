# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты записи разметок.

import unittest
import os

from poetry.apps.corpus.scripts.convertion.writer import Writer
from poetry.apps.corpus.scripts.convertion.reader import Reader, FileTypeEnum
from poetry.apps.corpus.scripts.settings import DICT_PATH, CLASSIFIER_PATH
from poetry.settings import BASE_DIR
from poetry.apps.corpus.scripts.accents.classifier import MLAccentClassifier
from poetry.apps.corpus.scripts.accents.dict import AccentDict
from poetry.apps.corpus.scripts.util.data import MARKUP_EXAMPLE


class TestWriter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accents_dict = AccentDict(DICT_PATH)
        cls.accents_classifier = MLAccentClassifier(CLASSIFIER_PATH, cls.accents_dict)

    def test_write(self):
        tempfile = os.path.join(BASE_DIR, "datasets", "temp.xml")
        markup = MARKUP_EXAMPLE
        Writer.write_markups(FileTypeEnum.XML, [markup], tempfile)
        processed_xml = Reader.read_markups(tempfile, FileTypeEnum.XML, is_processed=True)
        self.assertEqual(next(processed_xml), markup)
        processed_xml.close()
        os.remove(tempfile)
