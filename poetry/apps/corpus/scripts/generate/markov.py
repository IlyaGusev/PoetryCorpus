# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Модуль марковских цепей.

import os
import pickle
import xml.etree.ElementTree as etree
from collections import Counter, defaultdict

from poetry.settings import BASE_DIR
from poetry.apps.corpus.scripts.phonetics.phonetics import Phonetics
from poetry.apps.corpus.scripts.rhymes.rhymes import Rhymes
from poetry.apps.corpus.scripts.phonetics.phonetics_markup import CommonMixin
from poetry.apps.corpus.scripts.metre.metre_classifier import MetreClassifier


class Markov(CommonMixin):
    """
    Генерация стихов с помощью марковских цепей.
    """
    def __init__(self, accents_dict, accents_classifier):
        self.transitions = defaultdict(Counter)
        self.rhymes = Rhymes()
        self.short_words = {}

        # Делаем дамп модели для ускорения загрузки.
        dump_filename = os.path.join(BASE_DIR, "datasets", "markov.pickle")
        if os.path.isfile(dump_filename):
            with open(dump_filename, "rb") as f:
                markov = pickle.load(f)
                self.__dict__.update(markov.__dict__)
        else:
            root = etree.parse(os.path.join(BASE_DIR, "datasets", "corpus", "all.xml")).getroot()
            for item in root.findall("./item"):
                if item.find("./author").text == "Александр Пушкин":
                    markup, result = MetreClassifier.improve_markup(
                        Phonetics.process_text(item.find("./text").text, accents_dict), accents_classifier)
                    self.add_markup(markup)
            with open(dump_filename, "wb") as f:
                pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def generate_chain(self, words):
        """
        Генерация переходов в марковских цепях с учётом частотности.
        :param words: вершины цепи.
        :return: обновленные переходы.
        """
        for i in range(len(words) - 1):
            current_word = words[i]
            next_word = words[i+1]
            self.transitions[current_word][next_word] += 1
        return self.transitions

    def add_markup(self, markup):
        """
        Дополнение цепей на основе разметки.
        :param markup: разметка.
        """
        words = []
        for line in markup.lines:
            for word in line.words:
                words.append(word.get_short())
                self.short_words[word.get_short()] = word

        # Генерируем переходы.
        self.generate_chain(list(reversed(words)))

        # Заполняем словарь рифм.
        self.rhymes.add_markup(markup)
