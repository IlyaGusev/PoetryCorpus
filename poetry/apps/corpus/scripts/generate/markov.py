# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Модуль марковских цепей.

import os
import pickle
import sys
import xml.etree.ElementTree as etree
from collections import Counter, defaultdict
import numpy as np

from poetry.apps.corpus.scripts.generate.vocabulary import Vocabulary
from poetry.apps.corpus.scripts.phonetics.phonetics_markup import CommonMixin, Markup
from poetry.settings import BASE_DIR


class MarkovModelContainer(CommonMixin):
    """
    Марковские цепи.
    """
    def __init__(self):
        self.transitions = list()
        self.vocabulary = Vocabulary()

        # Делаем дамп модели для ускорения загрузки.
        dump_filename = os.path.join(BASE_DIR, "datasets", "markov.pickle")
        if os.path.isfile(dump_filename):
            with open(dump_filename, "rb") as f:
                markov = pickle.load(f)
                self.__dict__.update(markov.__dict__)
        else:
            sys.stdout.write("Starting\n")
            sys.stdout.flush()
            i = 0
            filename = os.path.join(BASE_DIR, "datasets", "corpus", "markup_dump.xml")
            for event, elem in etree.iterparse(filename, events=['end']):
                if event == 'end' and elem.tag == 'markup':
                    markup = Markup()
                    markup.from_xml(etree.tostring(elem, encoding='utf-8', method='xml'))
                    markup.text = markup.text.replace("\\n", "\n")
                    self.add_markup(markup)
                    elem.clear()
                    i += 1
                    if i % 500 == 0:
                        sys.stdout.write(str(i)+"\n")
                        sys.stdout.flush()

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
                is_added = self.vocabulary.add_word(word)
                if is_added:
                    self.transitions.append(Counter())
                words.append(self.vocabulary.get_word_index(word))

        # Генерируем переходы.
        self.generate_chain(list(reversed(words)))

    def get_model(self, word_indices):
        """
        Получение языковой модели.
        :param word_indices: индексы предыдущих слов.
        :return: языковая модель (распределение вероятностей для следующего слова).
        """
        l = len(self.transitions)
        if len(word_indices) == 0 or len(self.transitions[word_indices[-1]]) == 0:
            model = np.full(len(self.transitions), 1/l, dtype=np.float)
        else:
            transition = self.transitions[word_indices[-1]]
            s = sum(transition.values())
            model = np.zeros(len(self.transitions), dtype=np.float)
            for index, p in transition.items():
                model[index] = p/s
        return model
