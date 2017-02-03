# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты для модуля фонетики.

import unittest
import os

from poetry.settings import BASE_DIR
from poetry.apps.corpus.scripts.phonetics.accent_dict import AccentDict
from poetry.apps.corpus.scripts.phonetics.phonetics import Phonetics
from poetry.apps.corpus.scripts.phonetics.phonetics_markup import Syllable, Word, Markup, Line


class TestPhonetics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accent_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict"))

    def test_syllables(self):
        checks = {
            'я': [Syllable(0, 1, 0, 'я')],
            'в': [],
            'лдж': [],
            'кронв': [Syllable(0, 5, 0, 'кронв')],
            'он': [Syllable(0, 2, 0, 'он')],
            'когда': [Syllable(0, 2, 0, 'ко'), Syllable(2, 5, 1, 'гда')],
            'майка': [Syllable(0, 3, 0, 'май'), Syllable(3, 5, 1, 'ка')],
            'сонька': [Syllable(0, 4, 0, 'сонь'), Syllable(4, 6, 1, 'ка')],
            'соломка': [Syllable(0, 2, 0, 'со'), Syllable(2, 5, 1, 'лом'), Syllable(5, 7, 2, 'ка')],
            'изжить': [Syllable(0, 1, 0, 'и'), Syllable(1, 6, 1, 'зжить')],
            'виться': [Syllable(0, 2, 0, 'ви'), Syllable(2, 6, 1, 'ться')],
            'данный': [Syllable(0, 2, 0, 'да'), Syllable(2, 6, 1, 'нный')],
            'марка': [Syllable(0, 3, 0, 'мар'), Syllable(3, 5, 1, 'ка')],
            'зорька': [Syllable(0, 4, 0, 'зорь'), Syllable(4, 6, 1, 'ка')],
            'банка': [Syllable(0, 3, 0, 'бан'), Syllable(3, 5, 1, 'ка')],
            'банька': [Syllable(0, 4, 0, 'бань'), Syllable(4, 6, 1, 'ка')],
            'лайка': [Syllable(0, 3, 0, 'лай'), Syllable(3, 5, 1, 'ка')],
            'оттечь': [Syllable(0, 1, 0, 'о'), Syllable(1, 6, 1, 'ттечь')],
            'дяденька': [Syllable(0, 2, 0, 'дя'), Syllable(2, 6, 1, 'день'), Syllable(6, 8, 2, 'ка')],
            'подъезд': [Syllable(0, 2, 0, 'по'), Syllable(2, 7, 1, 'дъезд')],
            'морские': [Syllable(0, 3, 0, 'мор'), Syllable(3, 6, 1, 'ски'), Syllable(6, 7, 2, 'е')],
            'мерзкие': [Syllable(0, 3, 0, 'мер'), Syllable(3, 6, 1, 'зки'), Syllable(6, 7, 2, 'е')],
            'полный': [Syllable(0, 2, 0, 'по'), Syllable(2, 6, 1, 'лный')],
            'зародыш': [Syllable(0, 2, 0, 'за'), Syllable(2, 4, 1, 'ро'), Syllable(4, 7, 2, 'дыш')],
            'война': [Syllable(0, 3, 0, 'вой'), Syllable(3, 5, 1, 'на')],
        }

        for word, borders in checks.items():
            self.assertEqual(Phonetics.get_word_syllables(word), borders)

    def test_accents(self):
        checks = {
            'я': [0],
            'в': [],
            'он': [0],
            'майка': [1],
            'соломка': [3],
            'изжить': [3],
            'виться': [1],
            'данный': [1],
            'зорька': [1],
            'банка': [1],
            'оттечь': [3],
            'советского': [3],
            'союза': [2],
            'пора': [1, 3],
            'изжила': [5],
            'меда': [1]
        }

        for word, pos in checks.items():
            self.assertEqual(Phonetics.get_word_accent(word, self.accent_dict), pos)

    def test_process_text(self):
        text = "Соломка изжила себя.\n Пора виться майкой в."
        markup = Phonetics.process_text(text, self.accent_dict)
        new_markup = Markup()
        self.assertEqual(markup, new_markup.from_xml(markup.to_xml()))
        self.assertEqual(markup, Markup(text, [Line(0, 21, "Соломка изжила себя.", [
            Word(0, 7, "Соломка", [Syllable(0, 2, 0, "Со"),
                                   Syllable(2, 5, 1, "лом", 3),
                                   Syllable(5, 7, 2, "ка")]),
            Word(8, 14, "изжила", [Syllable(0, 1, 0, "и"),
                                   Syllable(1, 4, 1, "зжи"),
                                   Syllable(4, 6, 2, "ла", 5)]),
            Word(15, 19, "себя", [Syllable(0, 2, 0, "се"),
                                  Syllable(2, 4, 1, "бя", 3)])]), Line(21, 43, " Пора виться майкой в.",
           [Word(22, 26, "Пора", [Syllable(0, 2, 0, "По", 1),
                                  Syllable(2, 4, 1, "ра", 3)]),
            Word(27, 33, "виться", [Syllable(0, 2, 0, "ви", 1),
                                    Syllable(2, 6, 1, "ться")]),
            Word(34, 40, "майкой", [Syllable(0, 3, 0, "май", 1),
                                    Syllable(3, 6, 1, "кой")]),
            Word(41, 42, "в", [])
            ])]))
