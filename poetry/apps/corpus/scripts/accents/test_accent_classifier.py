# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты для модуля классификации ударений.

import unittest
import os

from poetry.settings import BASE_DIR
from poetry.apps.corpus.scripts.accents.classifier import MLAccentClassifier
from poetry.apps.corpus.scripts.accents.dict import AccentDict


class TestAccentClassifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accent_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict"))
        cls.accent_classifier = MLAccentClassifier(os.path.join(BASE_DIR, "datasets", "models"), cls.accent_dict)

    def test_accent_classifier(self):
        cv = self.accent_classifier.do_cross_val(self.accent_dict)
        self.assertGreater(cv[0], 0.75)
        self.assertGreater(cv[1], 0.85)
        print(cv)
        self.assertEqual(len([0, 2, 2, 1, 2, 2, 2, 1, 2]),
                         len([self.accent_classifier.classify_accent(word) for word in
                             ["волки", "перелив", "карачун", "пипярка", "пепелац", "гиппогриф",
                              "хвосторог", "стартап", "квинтолап"]]))
