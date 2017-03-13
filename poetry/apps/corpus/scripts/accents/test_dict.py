# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты для словаря ударений.

import unittest
import os

from poetry.settings import BASE_DIR
from poetry.apps.corpus.scripts.accents.dict import AccentDict, AccentType
from poetry.apps.corpus.scripts.util.preprocess import VOWELS


class TestAccentDict(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict")
        cls.trie_path = cls.path + ".trie"
        cls.txt_path = cls.path + ".txt"
        cls.dict = AccentDict(cls.path)

    def test_load_and_create(self):
        self.assertTrue(os.path.exists(self.txt_path))
        self.assertTrue(os.path.exists(self.trie_path))
        os.remove(self.trie_path)
        AccentDict(self.path)
        self.assertTrue(os.path.exists(self.trie_path))

    def test_get_accents(self):
        self.assertCountEqual(self.dict.get_accents("данный", AccentType.PRIMARY), [1])
        self.assertCountEqual(self.dict.get_accents("союза", AccentType.PRIMARY), [2])
        self.assertCountEqual(self.dict.get_accents("англосакс", AccentType.SECONDARY), [0])
        self.assertCountEqual(self.dict.get_accents("англосакс", AccentType.ANY), [0, 6])
        self.assertCountEqual(self.dict.get_accents("пора", AccentType.PRIMARY), [1, 3])

    def test_accent_only_in_vowels(self):
        for word, accents in self.dict.get_all():
            for accent in accents:
                self.assertIn(word[accent[0]], VOWELS)

