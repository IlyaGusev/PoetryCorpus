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
        model = {word: prob for word, prob in words_with_freq.items() if self.filter_word(word)}
        probabilities = list(model.values())
        s = sum(probabilities)
        l = len(probabilities)
        for word, p in model.items():
            model[word] = p/s if s != 0 else 1/l
        return model

    def filter_words(self, words):
        return [word for word in words if self.filter_word(word)]


class MetreFilter(Filter):
    def __init__(self, metre_pattern):
        self.metre_pattern = metre_pattern
        self.position = len(metre_pattern) - 1

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

    def pass_word(self, word):
        self.position -= len(word.syllables)

    def reset(self):
        self.position = len(self.metre_pattern) - 1


class RhymeFilter(Filter):
    def __init__(self, rhyme_pattern, letters_to_rhymes=None):
        self.rhyme_pattern = rhyme_pattern
        self.position = len(self.rhyme_pattern) - 1
        self.letters_to_rhymes = defaultdict(set)
        if letters_to_rhymes is not None:
            for letter, words in letters_to_rhymes.items():
                for word in words:
                    self.letters_to_rhymes[letter].add(word)

    def pass_word(self, word):
        self.letters_to_rhymes[self.rhyme_pattern[self.position]].add(word)
        self.position -= 1

    def filter_word(self, word):
        if len(word.syllables) <= 1:
            return False
        if len(self.letters_to_rhymes[self.rhyme_pattern[self.position]]) == 0:
            return True
        first_word = list(self.letters_to_rhymes[self.rhyme_pattern[self.position]])[0]
        is_rhyme = Rhymes.is_rhyme(first_word, word, score_border=5, syllable_number_border=2) and \
                   first_word.text != word.text
        return is_rhyme


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


class Generator(object):
    def __init__(self, transitions, short_words):
        self.transitions = transitions
        self.short_words = short_words

    def generate_line(self, transitions, metre_filter, rhyme_filter, seed_word=None):
        """
        Генерация одной строки с заданным количеством слогов.
        :param transitions: переходы в цепи.
        :param metre_filter: фильтр по метру.
        :param rhyme_filter: фильтр по рифме.
        :param seed_word: короткая версия первого слова.
        :return: получившаяся строка.
        """
        metre_filter.reset()
        model = {self.short_words[short]: 1 / len(transitions) for short in transitions.keys()}
        if seed_word is not None:
            model = {self.short_words[short]: prob for short, prob in transitions[seed_word].items()}
        model = self.__get_complete_model(model)
        model = rhyme_filter.filter_model(model)
        model = metre_filter.filter_model(model)
        # Если нет подходящих по рифме и метру слов, перезапускаем генерацию всего стихотворения.
        if len(model) == 0:
            return None, None
        last_word = Generator.__choose(model)
        metre_filter.pass_word(last_word)
        rhyme_filter.pass_word(last_word)
        text = last_word.text.lower()
        prev_step = last_word.get_short()

        while metre_filter.position >= 0:
            model = {self.short_words[short]: prob for short, prob in transitions[prev_step].items()}
            model = self.__get_complete_model(model)
            model = metre_filter.filter_model(model)
            word = Generator.__choose(model)
            metre_filter.pass_word(word)
            prev_step = word.get_short()
            text += " " + word.text.lower()
        return text, prev_step

    def generate_poem(self, metre_schema="-+", rhyme_pattern="abab", n_syllables=8, letters_to_rhymes=None):
        """
        Генерация стихотворения с выбранными параметрами.
        :param metre_schema: схема метра.
        :param rhyme_pattern: схема рифмы.
        :param n_syllables: количество слогов в строке.
        :return: стихотворение.
        """
        metre_pattern = ""
        while len(metre_pattern) <= n_syllables:
            metre_pattern += metre_schema
        metre_pattern = metre_pattern[:n_syllables]

        lines = []
        metre_filter = MetreFilter(metre_pattern)
        rhyme_filter = RhymeFilter(rhyme_pattern, letters_to_rhymes)
        seed_word = None
        while rhyme_filter.position >= 0:
            reversed_line, seed_word = self.generate_line(self.transitions, metre_filter, rhyme_filter, seed_word)
            if reversed_line is None:
                return self.generate_poem(metre_schema, rhyme_pattern, n_syllables, letters_to_rhymes)
            line = " ".join(reversed(reversed_line.split(" ")))
            lines.append(line)
        return "\n".join(reversed(lines)) + "\n"

    @staticmethod
    def __choose(model):
        return choice(list(model.keys()), 1, p=list(model.values()))[0]

    def __get_complete_model(self, model):
        for word in self.transitions.keys():
            if self.short_words[word] not in model:
                model[self.short_words[word]] = 0
        return model

    def generate_poem_by_line(self, accent_dict, accents_classifier, line, rhyme_pattern="aabb"):
        Phonetics.process_text(line, accent_dict)
        markup = Phonetics.process_text(line, accent_dict)
        markup, result = MetreClassifier.improve_markup(markup, accents_classifier)
        rhyme_word = markup.lines[0].words[-1]
        metre_pattern = result.lines_result[0].get_best_patterns()[result.metre]
        metre_pattern = metre_pattern.lower().replace("s", "+").replace("u", "-")
        count_syllables = sum(len(Phonetics.get_word_syllables(word)) for word in text_to_wordlist(line))
        metre_pattern = metre_pattern[:count_syllables]
        generated = self.generate_poem(metre_pattern, rhyme_pattern, len(metre_pattern), {rhyme_pattern[0]: {rhyme_word}})
        poem = line + "\n" + "\n".join(generated.split("\n")[1:])
        return poem
