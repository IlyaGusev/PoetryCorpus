# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты для разметки.

import unittest
from poetry.apps.corpus.scripts.util.data import MARKUP_EXAMPLE
from poetry.apps.corpus.scripts.main.markup import Markup


class TestMarkup(unittest.TestCase):
    def test_from_to(self):
        clean_markup = Markup()
        self.assertEqual(MARKUP_EXAMPLE, clean_markup.from_xml(MARKUP_EXAMPLE.to_xml()))
        clean_markup = Markup()
        self.assertEqual(MARKUP_EXAMPLE, clean_markup.from_json(MARKUP_EXAMPLE.to_json()))

