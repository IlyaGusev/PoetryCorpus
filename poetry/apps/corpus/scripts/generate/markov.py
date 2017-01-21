# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Модуль создания стихотворений на основе марковских цепей.

import os
import pickle
import xml.etree.ElementTree as etree
from numpy.random import choice
from collections import Counter, defaultdict

from poetry.settings import BASE_DIR
from poetry.apps.corpus.scripts.phonetics.phonetics import Phonetics
from poetry.apps.corpus.scripts.phonetics.phonetics_markup import CommonMixin
from poetry.apps.corpus.scripts.metre.metre_classifier import MetreClassifier


class Markov(CommonMixin):
    """
    Генерация стихов с помощью марковских цепей.
    """
    def __init__(self, accents_dict, accents_classifier):
        self.transitions = defaultdict(Counter)
        self.rhymes = defaultdict(Counter)
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
                    self.process_text(item.find("./text").text, accents_dict, accents_classifier)
            with open(dump_filename, "wb") as f:
                pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def process_text(self, text, accents_dict, accents_classifier):
        """
        Автоматическая разметка сырого текста.
        :param text: сам текст
        :param accents_dict: словарь ударений.
        :param accents_classifier: классификатор ударений.
        """
        markup = Phonetics.process_text(text, accents_dict)
        classifier = MetreClassifier(markup, accents_classifier)
        classifier.classify_metre()
        classifier.get_ml_results()
        markup = classifier.get_improved_markup()
        self.add_markup(markup)

    def generate_chain(self, words):
        """
        Генерация переходов в марковских цепях с учётом частотности.
        :param words: вершины цепи
        :return: обновленные переходы
        """
        for i in range(len(words) - 1):
            current_word = words[i]
            next_word = words[i+1]
            self.transitions[current_word][next_word] += 1
        return self.transitions

    def add_markup(self, markup):
        """
        Дополнение цепей на основе разметки.
        :param markup: разметка
        """
        words = []
        for line in markup.lines:
            for word in line.words:
                words.append(word.get_short())
                self.short_words[word.get_short()] = word

        # Генерируем переходы.
        self.generate_chain(list(reversed(words)))

        # Заполняем словарь рифм.
        rhymes = Phonetics.get_all_rhymes(markup, self.short_words, border=5)
        for short1, mapping in rhymes.items():
            for short2, freq in mapping.items():
                self.rhymes[short1][short2] += freq

    def filter_by_metre(self, collection, metre_pattern, n_syllables_min, n_syllables_max, position_in_pattern=-1):
        """
        Фильтрация по метру элементов коллекции из коротких версий слов из разметки.
        :param collection:  набор коротких версий слов
        :param metre_pattern: шаблон метра с длиной, равной количеству слогов в строке
        :param n_syllables_min: минимальное количество слогов в слове
        :param n_syllables_max: максимальное количество слогов в слове
        :param position_in_pattern: позиция в шаблоне метра, куда нужно вставить слово, -1 == вставить в конец
        :return: коллекция, фильрованная по метру
        """
        filtered_collection = dict()
        for short, freq in collection.items():
            word = self.short_words[short]
            pos = position_in_pattern if position_in_pattern != -1 else len(metre_pattern) - len(word.syllables)
            if len(word.syllables) > n_syllables_max or len(word.syllables) < n_syllables_min:
                continue

            good_word = True
            for i in range(len(word.syllables)):
                syllable = word.syllables[i]
                syllable_number = pos + i
                if len(word.syllables) >= 2 and syllable.accent != -1 and metre_pattern[syllable_number] == "-":
                    good_word = False
                    break
            if good_word:
                filtered_collection[short] = freq
        return filtered_collection

    def generate_line(self, transitions, n_syllables, seed_short=None, metre_pattern=None):
        """
        Генерация одной строки с заданным количеством слогов.
        :param transitions: переходы в цепи
        :param n_syllables: количество слогов в строке
        :param seed_short: короткая версия первого слова
        :param metre_pattern: шаблон метра с длиной, равной количеству слогов в строке
        :return: получившаяся строка
        """
        if seed_short is None:
            seed_short = choice(list(transitions.keys()), 1)[0]
        prev_step = seed_short
        seed_word = self.short_words[seed_short]
        text = seed_word.text.lower()
        syllables_count = len(seed_word.syllables)

        while syllables_count < n_syllables:
            if transitions.get(prev_step) is not None:
                transition = transitions[prev_step]
                transition = self.filter_by_metre(transition, metre_pattern, 1,
                                                  n_syllables-syllables_count, syllables_count)
                if len(transition) == 0:
                    return ""

                # Выбираем на основании частотности следующую вершину цепи
                candidates = list(transition.keys())
                weights = list(transition.values())
                weights = [w / sum(weights) for w in weights]
                next_word = self.short_words[choice(candidates, 1, p=weights)[0]]
            else:
                return ""

            prev_step = next_word.get_short()
            text += " " + next_word.text.lower()
            syllables_count += len(next_word.syllables)
        return text

    def generate_poem(self, metre_schema="-+", rhyme_schema="abab", n_syllables=8):
        """
        Генерация стихотворения с выбранными параметрами.
        :param metre_schema: схема метра
        :param rhyme_schema: схема рифмы
        :param n_syllables: количество слогов в строке
        :return: стихотворение
        """
        metre_pattern = ""
        while len(metre_pattern) < n_syllables:
            metre_pattern += metre_schema
        metre_pattern = metre_pattern[:n_syllables]

        poem = ""
        unique_letters = list(set(list(rhyme_schema)))
        rhyme_candidates = list(self.filter_by_metre(self.rhymes, metre_pattern, 2, n_syllables, -1).keys())

        letter_all_rhymes = {}
        for letter in unique_letters:
            letter_all_rhymes[letter] = []
            while len(letter_all_rhymes[letter]) < rhyme_schema.count(letter):
                seed_rhyme = choice(rhyme_candidates, 1)[0]
                rhyme_with_seed = set(self.filter_by_metre(self.rhymes[seed_rhyme], metre_pattern, 2, n_syllables, -1))
                rhyme_with_seed.add(seed_rhyme)
                letter_all_rhymes[letter] = list(rhyme_with_seed)

        for letter in rhyme_schema:
            generated = ""
            n_attempts = 0
            while generated == "":
                n_attempts += 1
                if n_attempts == 20:
                    print("Retry")
                    return self.generate_poem(metre_schema, rhyme_schema, n_syllables)
                seed = choice(letter_all_rhymes[letter], 1)[0]
                generated = self.generate_line(self.transitions, n_syllables,
                                               seed_short=seed, metre_pattern=metre_pattern)
                if generated != "":
                    letter_all_rhymes[letter].remove(seed)

            line = " ".join(reversed(generated.split(" ")))
            poem += line + "\n"
        return poem
