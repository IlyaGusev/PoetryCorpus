# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты считывателя разметок.

import unittest
import os

from poetry.apps.corpus.scripts.settings import DICT_PATH, CLASSIFIER_PATH, MARKUPS_DUMP_XML_PATH, POEMS_DUMP_PATH
from poetry.apps.corpus.scripts.convertion.reader import Reader, FileTypeEnum
from poetry.apps.corpus.scripts.accents.classifier import MLAccentClassifier
from poetry.apps.corpus.scripts.accents.dict import AccentDict
from poetry.apps.corpus.scripts.main.markup import Markup, Line, Word


class TestReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accents_dict = AccentDict(DICT_PATH)
        cls.accents_classifier = MLAccentClassifier(CLASSIFIER_PATH, cls.accents_dict)

    def test_read(self):
        if os.path.exists(MARKUPS_DUMP_XML_PATH):
            processed_xml = Reader.read_markups(MARKUPS_DUMP_XML_PATH, FileTypeEnum.XML, is_processed=True)
            self.__assert_markup_is_correct(next(processed_xml))

        unprocessed_xml = Reader.read_markups(POEMS_DUMP_PATH, FileTypeEnum.XML, is_processed=False,
                                              accents_dict=self.accents_dict,
                                              accents_classifier=self.accents_classifier)
        self.__assert_markup_is_correct(next(unprocessed_xml))

    def __assert_markup_is_correct(self, markup):
        print(markup)
        self.assertIsInstance(markup, Markup)
        self.assertIsNotNone(markup.text)
        self.assertNotEqual(markup.text, "")
        self.assertNotEqual(markup.lines, [])
        self.assertIsInstance(markup.lines[0], Line)
        self.assertIsInstance(markup.lines[0].words[0], Word)


