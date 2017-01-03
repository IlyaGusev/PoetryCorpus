# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты марковских цепей.

import unittest
import os
import xml.etree.ElementTree as etree
import pickle
import json

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

    def test_generate(self):
        dump_filename = os.path.join(BASE_DIR, "datasets", "markov.pickle")
        if os.path.isfile(dump_filename):
            with open(dump_filename, "rb") as f:
                markov = pickle.load(f)
        else:
            markov = Markov()
            tree = etree.parse(os.path.join(BASE_DIR, "datasets", "all.xml"))
            root = tree.getroot()
            for text in root.findall(".//text"):
                content = text.text
                markup = Phonetics.process_text(content, self.accents_dict)
                classifier = MetreClassifier(markup, self.accents_classifier)
                classifier.classify_metre()
                classifier.get_ml_results()
                markup = classifier.get_improved_markup()
                markov.add_text(markup)
            with open(dump_filename, "wb") as f:
                pickle.dump(markov, f, pickle.HIGHEST_PROTOCOL)

        print(markov.generate_poem(metre_schema="-+", rhyme_schema="abab", n_lines=4, n_syllables=8))
        print(markov.generate_poem(metre_schema="-+", rhyme_schema="abab", n_lines=4, n_syllables=8))
        print(markov.generate_poem(metre_schema="-+", rhyme_schema="ababcc", n_lines=6, n_syllables=10))
        print(markov.generate_poem(metre_schema="-+", rhyme_schema="ababcc", n_lines=6, n_syllables=10))
