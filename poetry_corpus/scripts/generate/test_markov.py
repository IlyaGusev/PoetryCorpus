# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты марковских цепей.

import unittest
import os

from poetry_corpus.settings import BASE_DIR
from poetry_corpus.scripts.generate.markov import Markov
from poetry_corpus.scripts.phonetics.accent_classifier import AccentClassifier
from poetry_corpus.scripts.phonetics.accent_dict import AccentDict


class TestMarkovChains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accents_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict.txt"))
        cls.accents_classifier = AccentClassifier(os.path.join(BASE_DIR, "datasets", "models"), cls.accents_dict)

    def test_generate(self):
        markov = Markov(self.accents_dict, self.accents_classifier)
        print(markov.generate_poem(metre_schema="-+", rhyme_schema="abab", n_syllables=8))
        print(markov.generate_poem(metre_schema="-+", rhyme_schema="abab", n_syllables=8))
        print(markov.generate_poem(metre_schema="-+", rhyme_schema="abba", n_syllables=8))
        print(markov.generate_poem(metre_schema="-+", rhyme_schema="ababcc", n_syllables=10))
