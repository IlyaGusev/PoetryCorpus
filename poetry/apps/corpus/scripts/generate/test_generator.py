# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты марковских цепей.

import unittest
import os

from poetry.settings import BASE_DIR
from poetry.apps.corpus.scripts.generate.markov import MarkovModelContainer
from poetry.apps.corpus.scripts.generate.generator import Generator


class TestMarkovChains(unittest.TestCase):
    def test_generate(self):
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
        # poem5 = generator.generate_poem_by_line(self.accents_dict, self.accents_classifier,
        #                                         "Забывши волнения жизни мятежной,")
        # print(poem5)
        # try:
        #     poem6 = generator.generate_poem_by_line(self.accents_dict, self.accents_classifier,
        #                                             "Просто первая строка")
        #     print(poem6)
        # except RuntimeError as e:
        #     print(e)


