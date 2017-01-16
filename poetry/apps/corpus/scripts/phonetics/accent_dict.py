# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Класс для удобной работы со словарём ударений.

import os
import pickle

from poetry.apps.corpus.scripts.preprocess import normilize_line


class AccentDict:
    """
    Класс данных, для сериализации словаря как dict'а и быстрой загрузки в память.
    """
    def __init__(self, accents_filename):
        self.data = dict()
        self.load(accents_filename)

    def load(self, filename):
        """
        Загрузка словаря из файла. Если уже есть его сериализация в .pickle файле, берём из него.

        :param filename: имя файла с оригинальным словарём.
        """
        dump_file = os.path.splitext(filename)[0] + '.pickle'
        if os.path.isfile(dump_file):
            with open(dump_file, 'rb') as p:
                self.data = pickle.load(p)
        else:
            with open(filename, 'r', encoding='utf-8') as f:
                words = f.readlines()
                for line in words:
                    for word in line.split("#")[1].split(","):
                        if self.data.get(normilize_line(word)):
                            self.data[normilize_line(word)].append(word.strip())
                        else:
                            self.data[normilize_line(word)] = [word.strip()]
                with open(dump_file, 'wb') as p:
                    pickle.dump(self.data, p)

    def get(self, word):
        """
        Обёртка над data.get().

        :param word: слово, которое мы хотим посмотреть в словаре.
        :return forms: массив форм с разными ударениями.
        """
        return self.data.get(word)
