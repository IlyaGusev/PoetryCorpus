# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты марковских цепей.

import unittest
import os
import xml.etree.ElementTree as etree

from poetry_corpus.settings import BASE_DIR
from poetry_corpus.scripts.generate.markov import Markov
from poetry_corpus.scripts.phonetics.phonetics import Phonetics
from poetry_corpus.scripts.phonetics.accent_classifier import AccentClassifier
from poetry_corpus.scripts.phonetics.accent_dict import AccentDict
from poetry_corpus.scripts.metre.metre_classifier import MetreClassifier


class TestMarkovChains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accents_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict.txt"))
        cls.accents_classifier = AccentClassifier(os.path.join(BASE_DIR, "datasets", "models"), cls.accents_dict)

    # def test_markov_add_and_generate(self):
    #
    #     text = "Горит восток зарёю новой.\n" \
    #            "Уж на равнине, по холмам\n" \
    #            "Грохочут пушки. Дым багровый\n" \
    #            "Кругами всходит к небесам.\n" \
    #            "Буря мглою небо кроет,\n" \
    #            "Вихри снежные крутя;\n" \
    #            "То, как зверь, она завоет,\n" \
    #            "То заплачет, как дитя..."
    #     markov1 = Markov(n_prev=1)
    #     markov2 = Markov(n_prev=2)
    #     markov1.add_text(text)
    #     markov2.add_text(text)
        # self.assertEqual(len(markov1.generate_markov_text(size=10).split(" ")), 10)
        # self.assertEqual(len(markov1.generate_markov_text(size=10).split(" ")), 10)

    def test_generate(self):
        markov = Markov(n_prev=1)
        tree = etree.parse("datasets/all.xml")
        root = tree.getroot()
        for text in root.findall(".//text")[:2000]:
            content = text.text
            markup = Phonetics.process_text(content, self.accents_dict)
            classifier = MetreClassifier(markup, self.accents_classifier)
            classifier.classify_metre()
            classifier.get_ml_results()
            markup = classifier.get_improved_markup()
            markov.add_text(markup)
        for i in range(10):
            print(markov.generate_poem())
