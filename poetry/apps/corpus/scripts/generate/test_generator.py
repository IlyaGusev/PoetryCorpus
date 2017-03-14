# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты марковских цепей.

import unittest
import os

from poetry.settings import BASE_DIR
from poetry.apps.corpus.scripts.generate.markov import MarkovModelContainer
from poetry.apps.corpus.scripts.generate.generator import Generator
from poetry.apps.corpus.scripts.accents.classifier import MLAccentClassifier
from poetry.apps.corpus.scripts.accents.dict import AccentDict


class TestMarkovChains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accents_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict"))
        cls.accents_classifier = MLAccentClassifier(os.path.join(BASE_DIR, "datasets", "models"), cls.accents_dict)

    def test_generate(self):
        if os.path.exists(os.path.join(BASE_DIR, "datasets", "corpus", "markup_dump.xml")):
            markov = MarkovModelContainer()
            generator = Generator(markov, markov.vocabulary)
            poem1 = generator.generate_poem(metre_schema="-+", rhyme_pattern="abab", n_syllables=8)
            self.assertEqual(len(poem1.split("\n")), 5)
            print(poem1)
            poem2 = generator.generate_poem(metre_schema="-+", rhyme_pattern="abab", n_syllables=8)
            self.assertEqual(len(poem2.split("\n")), 5)
            print(poem2)
            poem3 = generator.generate_poem(metre_schema="-+", rhyme_pattern="abba", n_syllables=8)
            self.assertEqual(len(poem3.split("\n")), 5)
            print(poem3)
            poem4 = generator.generate_poem(metre_schema="-+", rhyme_pattern="ababcc", n_syllables=10)
            self.assertEqual(len(poem4.split("\n")), 7)
            print(poem4)
            poem5 = generator.generate_poem_by_line(self.accents_dict, self.accents_classifier,
                                                    "Забывши волнения жизни мятежной,")
            print(poem5)
            poem6 = generator.generate_poem_by_line(self.accents_dict, self.accents_classifier,
                                                    "Просто первая строка")
            print(poem6)


