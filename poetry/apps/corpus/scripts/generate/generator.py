# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Модуль создания стихотворений.

from numpy.random import choice

from poetry.apps.corpus.scripts.phonetics.phonetics import Phonetics
from poetry.apps.corpus.scripts.metre.metre_classifier import MetreClassifier
from poetry.apps.corpus.scripts.preprocess import text_to_wordlist
from poetry.apps.corpus.scripts.generate.filters import MetreFilter, RhymeFilter


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

    def generate_poem(self, metre_schema="-+", rhyme_pattern="abab", n_syllables=8,
                      letters_to_rhymes=None, n_attempts=0):
        """
        Генерация стихотворения с выбранными параметрами.
        :param metre_schema: схема метра.
        :param rhyme_pattern: схема рифмы.
        :param n_syllables: количество слогов в строке.
        :return: стихотворение.
        """
        if n_attempts >= 10:
            raise RuntimeError("Не смог сгенерировать. Не хватает подходящих по рифме и метру слов. ")
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
                n_attempts += 1
                return self.generate_poem(metre_schema, rhyme_pattern, n_syllables, letters_to_rhymes, n_attempts)
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
