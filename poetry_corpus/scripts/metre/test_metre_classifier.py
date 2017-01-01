# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты к классификатору метра.

import unittest

from poetry_corpus.scripts.phonetics.accent_dict import AccentDict
from poetry_corpus.scripts.phonetics.phonetics import Phonetics

from poetry_corpus.scripts.metre.metre_classifier import MetreClassifier


class TestMetreClassifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accent_dict = AccentDict("../datasets/dicts/accents_dict.txt")

    def test_metre_classifier(self):

        text = "Горит восток зарёю новой.\n" \
               "Уж на равнине, по холмам\n" \
               "Грохочут пушки. Дым багровый\n" \
               "Кругами всходит к небесам."
        clf = MetreClassifier(Phonetics.process_text(text, self.accent_dict))
        result_metre = clf.classify_metre()
        self.assertEqual(result_metre, "iambos")

        text = "Буря мглою небо кроет,\n" \
               "Вихри снежные крутя;\n" \
               "То, как зверь, она завоет,\n" \
               "То заплачет, как дитя..."
        clf = MetreClassifier(Phonetics.process_text(text, self.accent_dict))
        result_metre = clf.classify_metre()
        self.assertEqual(result_metre, "choreios")

        clf.get_improved_markup()
