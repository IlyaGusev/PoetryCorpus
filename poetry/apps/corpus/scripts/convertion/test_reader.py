# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты считывателя разметок.

import unittest
import os

from poetry.settings import BASE_DIR
from poetry.apps.corpus.scripts.convertion.reader import SourceReader, SourceTypeEnum
from poetry.apps.corpus.scripts.accents.classifier import MLAccentClassifier
from poetry.apps.corpus.scripts.accents.dict import AccentDict
from poetry.apps.corpus.scripts.main.markup import Markup, Line, Word


class TestReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accents_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict"))
        cls.accents_classifier = MLAccentClassifier(os.path.join(BASE_DIR, "datasets", "models"), cls.accents_dict)

    def test_read(self):
        processed_xml = SourceReader.read_markups(SourceTypeEnum.XML,
                                                  is_folder=False, is_processed=True,
                                                  path=os.path.join(BASE_DIR, "datasets",
                                                                    "corpus", "markup_dump.xml"))
        unprocessed_xml = SourceReader.read_markups(SourceTypeEnum.XML,
                                                    is_folder=False, is_processed=False,
                                                    path=os.path.join(BASE_DIR, "datasets", "corpus", "all.xml"),
                                                    accents_dict=self.accents_dict,
                                                    accents_classifier=self.accents_classifier)
        self.__assert_markup_is_correct(next(processed_xml))
        self.__assert_markup_is_correct(next(unprocessed_xml))

    def __assert_markup_is_correct(self, markup):
        print(markup)
        self.assertIsInstance(markup, Markup)
        self.assertIsNotNone(markup.text)
        self.assertNotEqual(markup.text, "")
        self.assertNotEqual(markup.lines, [])
        self.assertIsInstance(markup.lines[0], Line)
        self.assertIsInstance(markup.lines[0].words[0], Word)


