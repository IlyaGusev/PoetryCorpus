# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Класс рифм.

import os
import pickle
import xml.etree.ElementTree as etree
from collections import Counter, defaultdict

from poetry.settings import BASE_DIR
from poetry.apps.corpus.scripts.phonetics.phonetics import Phonetics
from poetry.apps.corpus.scripts.metre.metre_classifier import MetreClassifier
from poetry.apps.corpus.scripts.preprocess import VOWELS
from poetry.apps.corpus.scripts.phonetics.phonetics_markup import Word


class Rhymes(object):
    """
    Поиск, обработка и хранение рифм.
    """
    def __init__(self):
        self.rhymes = defaultdict(set)
        self.short_words = {}

    def add_markup(self, markup):
        """
        Добавление рифм из разметки.
        :param markup: разметка.
        """
        rhymes = Rhymes.get_markup_rhymes(markup, self.short_words, border=5)
        for short1, rhymes in rhymes.items():
            for short2 in rhymes:
                self.rhymes[short1].add(short2)

    def save(self, filename):
        """
        Сохранение состояния данных.
        :param filename: путь к модели.
        """
        with open(filename, "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def load(self, filename):
        """
        Загрузка состояния данных.
        :param filename: путь к модели.
        """
        with open(filename, "rb") as f:
            markov = pickle.load(f)
            self.__dict__.update(markov.__dict__)

    def get_word_rhymes(self, word):
        """
        Поиск рифмы для данного слова.
        :param word: слово.
        :return: список рифм.
        """
        rhymes = set(self.rhymes[word.get_short()])
        for short_rhyme in self.rhymes.keys():
            if self.is_rhyme(self.short_words[short_rhyme], word, syllable_number_border=10):
                rhymes.add(short_rhyme)
        return list(rhymes)

    def get_words(self):
        """
        Поулчить все слова.
        :return: список слов.
        """
        return [self.short_words[word] for word in self.rhymes.keys()]

    def get_rhymes(self, short_word):
        """
        Поулчить рифмы данного слова.
        :return: список рифм данному слову.
        """
        return [self.short_words[word] for word in list(self.rhymes[short_word])]

    @staticmethod
    def get_rhyme_profile(word):
        """
        Получение профиля рифмовки (набора признаков для сопоставления).
        :param word: уже акцентуированное слово (Word).
        :return profile: профиль рифмовки.
        """
        # TODO: Переход на фонетическое слово, больше признаков.
        syllable_number = 0
        accented_syllable = ''
        next_syllable = ''
        next_char = ''
        syllables = list(reversed(word.syllables))
        for i in range(len(syllables)):
            syllable = syllables[i]
            if syllable.accent != -1:
                if i != 0:
                    next_syllable = syllables[i - 1].text
                accented_syllable = syllables[i].text
                if syllable.accent + 1 < len(word.text):
                    next_char = word.text[syllable.accent + 1]
                syllable_number = i
                break
        return syllable_number, accented_syllable, next_syllable, next_char

    @staticmethod
    def is_rhyme(word1, word2, score_border=4, syllable_number_border=2):
        """
        Проверка рифмованности 2 слов.
        :param word1: первое слово для проверки рифмы, уже акцентуированное (Word).
        :param word2: второе слово для проверки рифмы, уже акцентуированное (Word).
        :param score_border: граница определния рифмы, чем выше, тем строже совпадение.
        :param syllable_number_border: ограничение на номер слога с конца, на который падает ударение.
        :return result: является рифмой или нет.
        """
        features1 = Rhymes.get_rhyme_profile(word1)
        features2 = Rhymes.get_rhyme_profile(word2)
        count_equality = 0
        for i in range(len(features1[1])):
            for j in range(i, len(features2[1])):
                if features1[1][i] == features2[1][j]:
                    if features1[1][i] in VOWELS:
                        count_equality += 3
                    else:
                        count_equality += 1
        if features1[2] == features2[2] and features1[2] != '':
            count_equality += 2
        elif features1[3] == features2[3] and features1[3] != '':
            count_equality += 1
        return features1[0] == features2[0] and count_equality >= score_border and \
               features1[0] <= syllable_number_border

    @staticmethod
    def get_markup_rhymes(markup, short_words, border=4):
        """
        Получение всех рифм в разметке.
        :param markup: разметка.
        :param short_words: сопоставление коротких версии слов в разметке с нормальными версиями.
        :param border: граница определния рифмы, чем выше, тем строже совпадение.
        :return result: словарь всех рифм, в коротком предсатвлении.
        """
        rhymes = defaultdict(set)
        rhyme_candidates = []
        for line in markup.lines:
            if len(line.words) != 0:
                rhyme_candidates.append(line.words[-1])
        for i in range(len(rhyme_candidates)):
            for j in range(i + 1, len(rhyme_candidates)):
                words = (rhyme_candidates[i], rhyme_candidates[j])
                if Rhymes.is_rhyme(words[0], words[1], border):
                    shorts = (words[0].get_short(), words[1].get_short())
                    short_words[shorts[0]] = words[0]
                    short_words[shorts[1]] = words[1]
                    for item in [shorts, tuple(reversed(shorts))]:
                        rhymes[item[0]].add(item[1])
        return rhymes

    @staticmethod
    def get_all_rhymes(accents_dict, accents_classifier):
        """
        Получние рифм всего корпуса.
        :param accents_dict: словарь ударений.
        :param accents_classifier: классификатор ударений.
        :return: объект Rhymes.
        """
        root = etree.parse(os.path.join(BASE_DIR, "datasets", "corpus", "all.xml")).getroot()
        dump_filename = os.path.join(BASE_DIR, "datasets", "rhymes.pickle")
        rhymes = Rhymes()
        if os.path.isfile(dump_filename):
            rhymes.load(dump_filename)
        else:
            for item in root.findall("./item"):
                markup = Phonetics.process_text(item.find("./text").text, accents_dict)
                markup = MetreClassifier.improve_markup(markup, accents_classifier)
                rhymes.add_markup(markup)
            rhymes.save(dump_filename)
        return rhymes
