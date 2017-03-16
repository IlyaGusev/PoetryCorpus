# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты записи разметок.

import unittest
import os

from poetry.apps.corpus.scripts.convertion.writer import DestinationWriter, DestinationTypeEnum
from poetry.apps.corpus.scripts.convertion.reader import SourceReader, SourceTypeEnum
from poetry.settings import BASE_DIR
from poetry.apps.corpus.scripts.accents.classifier import MLAccentClassifier
from poetry.apps.corpus.scripts.accents.dict import AccentDict
from poetry.apps.corpus.scripts.util.data import MARKUP_EXAMPLE


class TestWriter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accents_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict"))
        cls.accents_classifier = MLAccentClassifier(os.path.join(BASE_DIR, "datasets", "models"), cls.accents_dict)

    def test_write(self):
        tempfile = os.path.join(BASE_DIR, "datasets", "temp.xml")
        markup = MARKUP_EXAMPLE
        DestinationWriter.write_markups(DestinationTypeEnum.XML, [markup], tempfile)
        processed_xml = SourceReader.read_markups(SourceTypeEnum.XML,
                                                  is_folder=False, is_processed=True,
                                                  path=tempfile)
        self.assertEqual(next(processed_xml), markup)
        processed_xml.close()
        os.remove(tempfile)
