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
from poetry.apps.corpus.scripts.rhymes.rhymes import Rhymes
from poetry.apps.corpus.scripts.phonetics.phonetics_markup import CommonMixin
from poetry.apps.corpus.scripts.metre.metre_classifier import MetreClassifier
from poetry.apps.corpus.scripts.preprocess import text_to_wordlist


class Filter(object):
    def filter_word(self, word):
        raise NotImplementedError()

    def filter_model(self, words_with_freq):
        return {word: prob for word, prob in words_with_freq.items() if self.filter_word(word)}

    def filter_words(self, words):
        return [word for word in words if self.filter_word(word)]


class MetreFilter(Filter):
    def __init__(self, metre_pattern, syllables_min):
        self.position = len(metre_pattern) - 1
        self.syllables_min = syllables_min
        self.metre_pattern = metre_pattern

    def filter_word(self, word):
        syllables_count = len(word.syllables)
        if syllables_count > self.position + 1:
            return False
        for i in range(syllables_count):
            syllable = word.syllables[i]
            syllable_number = self.position - syllables_count + i + 1
            if syllables_count >= 2 and syllable.accent == -1 and self.metre_pattern[syllable_number] == "+":
                for j in range(syllables_count):
                    other_syllable = word.syllables[j]
                    other_syllable_number = other_syllable.number - syllable.number + syllable_number
                    if i != j and other_syllable.accent != -1 and self.metre_pattern[other_syllable_number] == "-":
                        return False
        return True

    def filter_sentence(self, words):
        for word in words:
            if not self.filter_word(word):
                self.reset()
                return False
            self.position -= len(word.syllables)
        self.reset()
        return True

    def reset(self):
        self.position = len(self.metre_pattern) - 1


class RhymeFilter(Filter):
    def __init__(self, previous_rhyme):
        self.previous_rhyme = previous_rhyme

    def filter_word(self, word):
        return Rhymes.is_rhyme(self.previous_rhyme, word, score_border=4, syllable_number_border=10)


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

    def generate_line(self, transitions, metre_filter, seed_short=None):
        """
        Генерация одной строки с заданным количеством слогов.
        :param transitions: переходы в цепи.
        :param metre_filter: фильтр.
        :param seed_short: короткая версия первого слова.
        :return: получившаяся строка.
        """
        if seed_short is None:
            seed_short = choice(list(transitions.keys()), 1)[0]
        prev_step = seed_short
        seed_word = self.short_words[seed_short]
        text = seed_word.text.lower()
        syllables_count = len(seed_word.syllables)

        while syllables_count < len(metre_filter.metre_pattern):
            if transitions.get(prev_step) is not None:
                transition = transitions[prev_step]
                transition_full = {self.short_words[short]: prob for short, prob in transition.items()}
                transition = metre_filter.filter_model(transition_full)

                if len(transition) == 0:
                    return ""

                # Выбираем на основании частотности следующую вершину цепи
                candidates = list(transition.keys())
                weights = list(transition.values())
                weights = [w / sum(weights) for w in weights]
                next_word = choice(candidates, 1, p=weights)[0]
            else:
                return ""

            prev_step = next_word.get_short()
            text += " " + next_word.text.lower()
            syllables_count += len(next_word.syllables)
        return text

    def generate_poem(self, metre_schema="-+", rhyme_schema="abab", n_syllables=8, seeds=None):
        """
        Генерация стихотворения с выбранными параметрами.
        :param metre_schema: схема метра.
        :param rhyme_schema: схема рифмы.
        :param n_syllables: количество слогов в строке.
        :return: стихотворение.
        """
        metre_pattern = ""
        while len(metre_pattern) <= n_syllables:
            metre_pattern += metre_schema
        metre_pattern = metre_pattern[:n_syllables]

        metre_filter = MetreFilter(metre_pattern, syllables_min=2)
        letters_to_rhymes = self.__generate_rhymes(rhyme_schema, metre_filter, self.rhymes.get_words(), seeds)
        return self.__expand_rhymes(rhyme_schema, metre_filter, letters_to_rhymes, seeds)

    def __generate_rhymes(self, rhyme_schema, metre_filter, candidates, seeds=None):
        seeds = {} if seeds is None else seeds
        letters_to_rhymes = defaultdict(list)
        unique_letters = list(set(list(rhyme_schema)))
        for letter in unique_letters:
            count_letter = sum(letter == ch for ch in rhyme_schema)
            n_attempts = 0
            while len(letters_to_rhymes[letter]) < count_letter:
                seed = seeds[letter] if letter in seeds else choice(candidates, 1)[0]
                if letter in seeds:
                    n_attempts += 1
                    if n_attempts == 20:
                        seeds = {}
                rhymes = self.rhymes.get_rhymes(seed.get_short())
                letters_to_rhymes[letter] = metre_filter.filter_words(list(set([seed, ] + rhymes)))
        return letters_to_rhymes

    def __expand_rhymes(self, rhyme_schema, metre_filter, letters_to_rhymes, seeds=None):
        poem = ""
        for letter in rhyme_schema:
            generated = ""
            n_attempts = 0
            while generated == "":
                n_attempts += 1
                if n_attempts == 20:
                    print("Retry")
                    return self.generate_poem(metre_filter.metre_pattern, rhyme_schema,
                                              len(metre_filter.metre_pattern), seeds)
                seed = choice(letters_to_rhymes[letter], 1)[0]
                generated = self.generate_line(self.transitions, metre_filter, seed_short=seed.get_short())
                if generated != "":
                    letters_to_rhymes[letter].remove(seed)
            poem += " ".join(reversed(generated.split(" "))) + "\n"
        return poem

    def generate_poem_by_line(self, accent_dict, accents_classifier, line, rhyme_schema="aabb"):
        Phonetics.process_text(line, accent_dict)
        markup = Phonetics.process_text(line, accent_dict)
        markup, result = MetreClassifier.improve_markup(markup, accents_classifier)
        rhyme_word = markup.lines[0].words[-1]
        metre_pattern = result.lines_result[0].get_best_patterns()[result.metre]
        metre_pattern = metre_pattern.lower().replace("s", "+").replace("u", "-")
        count_syllables = sum(len(Phonetics.get_word_syllables(word)) for word in text_to_wordlist(line))
        metre_pattern = metre_pattern[:count_syllables]
        self.short_words[rhyme_word.get_short()] = rhyme_word
        self.rhymes.short_words[rhyme_word.get_short()] = rhyme_word
        self.rhymes.rhymes[rhyme_word.get_short()] = self.rhymes.get_word_rhymes(rhyme_word)
        generated = self.generate_poem(metre_pattern, rhyme_schema, len(metre_pattern), {rhyme_schema[0]: rhyme_word})
        poem = line + "\n".join(generated.split("\n")[1:])
        return poem
