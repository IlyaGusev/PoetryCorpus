# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Класс для удобной работы со словарём ударений.

import datrie
import os

from poetry.apps.corpus.scripts.util.preprocess import CYRRILIC_LOWER_VOWELS, CYRRILIC_LOWER_CONSONANTS


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
        dump_file = filename + '.trie'

        if os.path.isfile(dump_file):
            self.data = datrie.Trie.load(dump_file)
        else:
            with open(filename+".txt", 'r', encoding='utf-8') as f:
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
                                if word[i] == "`":
                                    accents.append((pos, 1))
                                else:
                                    accents.append((pos, 0))
                                continue
                            if word[i] == "ё":
                                accents.append((pos, 0))
                            clean_word += word[i]
                            pos += 1
                        self.__update(clean_word, accents)
            self.data.save(dump_file)

    def save(self, filename):
        dump_file = os.path.splitext(filename)[0] + '.trie'
        self.data.save(dump_file)

    def get_accents(self, word, accent_type=None):
        """
        Обёртка над data.get().
        :param word: слово, которое мы хотим посмотреть в словаре.
        :param accent_type: тип ударения.
        :return forms: массив всех ударений.
        """
        if word in self.data:
            if accent_type is None:
                return [i[0] for i in self.data[word]]
            elif accent_type == "primary":
                return [i[0] for i in self.data[word] if i[1] == 0]
            else:
                return [i[0] for i in self.data[word] if i[1] == 1]
        return []

    def __update(self, word, accent_pairs):
        """
        Обновление словаря.
        :param word: слово.
        :param accent_pairs: набор ударений.
        """
        if word not in self.data:
            self.data[word] = set([accent_pair for accent_pair in accent_pairs])
        else:
            self.data[word].update(accent_pairs)
