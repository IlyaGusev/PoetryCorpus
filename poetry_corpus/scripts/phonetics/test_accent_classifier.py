# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты для модуля классификации ударений.

import unittest

from poetry_corpus.scripts.phonetics.accent_classifier import AccentClassifier
from poetry_corpus.scripts.phonetics.accent_dict import AccentDict


class TestAccentClassifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accent_dict = AccentDict("../datasets/dicts/accents_dict.txt")
        cls.accent_classifier = AccentClassifier("../datasets/models", cls.accent_dict)

    def test_accent_classifier(self):
        self.assertEqual(len([0, 2, 2, 1, 2, 2, 2, 1, 2]),
                         len(self.accent_classifier.classify_accent(
                             ["волки", "перелив", "карачун", "пипярка", "пепелац", "гиппогриф",
                              "хвосторог", "стартап", "квинтолап"])))
