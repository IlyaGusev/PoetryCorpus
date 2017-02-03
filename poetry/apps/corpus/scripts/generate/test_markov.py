# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты марковских цепей.

import unittest
import os

from poetry.settings import BASE_DIR
from poetry.apps.corpus.scripts.generate.markov import Markov
from poetry.apps.corpus.scripts.phonetics.accent_classifier import AccentClassifier
from poetry.apps.corpus.scripts.phonetics.accent_dict import AccentDict


class TestMarkovChains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accents_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict"))
        cls.accents_classifier = AccentClassifier(os.path.join(BASE_DIR, "datasets", "models"), cls.accents_dict)

    def test_generate(self):
        markov = Markov(self.accents_dict, self.accents_classifier)
        poem1 = markov.generate_poem(metre_schema="-+", rhyme_schema="abab", n_syllables=8)
        self.assertEqual(len(poem1.split("\n")), 5)
        print(poem1)
        poem2 = markov.generate_poem(metre_schema="-+", rhyme_schema="abab", n_syllables=8)
        self.assertEqual(len(poem2.split("\n")), 5)
        print(poem2)
        poem3 = markov.generate_poem(metre_schema="-+", rhyme_schema="abba", n_syllables=8)
        self.assertEqual(len(poem3.split("\n")), 5)
        print(poem3)
        poem4 = markov.generate_poem(metre_schema="-+", rhyme_schema="ababcc", n_syllables=10)
        self.assertEqual(len(poem4.split("\n")), 7)
        print(poem4)
