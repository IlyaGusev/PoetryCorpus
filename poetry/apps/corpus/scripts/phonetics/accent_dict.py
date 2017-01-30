# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Класс для удобной работы со словарём ударений.

import os
import datrie

from poetry.apps.corpus.scripts.preprocess import CYRRILIC_LOWER_VOWELS, CYRRILIC_LOWER_CONSONANTS


class AccentDict:
    """
    Класс данных, для сериализации словаря как dict'а и быстрой загрузки в память.
    """
    def __init__(self, accents_filename):
        self.data = datrie.Trie(CYRRILIC_LOWER_VOWELS+CYRRILIC_LOWER_CONSONANTS+"-")
        self.load(accents_filename)

    def load(self, filename):
        """
        Загрузка словаря из файла. Если уже есть его сериализация в .trie файле, берём из него.
        :param filename: имя файла с оригинальным словарём.
        """
        dump_file = os.path.splitext(filename)[0] + '.trie'

        if os.path.isfile(dump_file):
            self.data = datrie.Trie.load(dump_file)
        else:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    for word in line.split("#")[1].split(","):
                        word = word.strip()
                        pos = 0
                        accents = []
                        clean_word = ""
                        for i in range(len(word)):
                            if word[i] == "'" or word[i] == "`":
                                pos -= 1
                                accents.append(pos)
                                continue
                            if word[i] == "ё":
                                accents.append(pos)
                            clean_word += word[i]
                            pos += 1
                        self.update(clean_word, accents)
            self.data.save(dump_file)

    def get_accents(self, word):
        """
        Обёртка над data.get().
        :param word: слово, которое мы хотим посмотреть в словаре.
        :return forms: массив форм с разными ударениями.
        """
        if word in self.data:
            return list(self.data[word])
        return []

    def update(self, word, accents):
        """
        Обновление словаря.
        :param word: слово.
        :param accents: набор ударений.
        """
        if word not in self.data:
            self.data[word] = set(accents)
        else:
            self.data[word].update(accents)
