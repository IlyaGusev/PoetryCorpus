# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Модуль разбивки на слоги, проставления ударений и получения начальной разметки.

from poetry_corpus.scripts.phonetics.phonetics_markup import Syllable, Word, Markup, Line
from poetry_corpus.scripts.preprocess import count_vowels, get_first_vowel_position, VOWELS, CLOSED_SYLLABLE_CHARS


class Phonetics:
    """
    Класс-механизм для фонетического анализа слова.
    """
    @staticmethod
    def get_word_syllables(word):
        """
        Разделение слова на слоги.

        :param word: слово для разбивки на слоги
        :return syllables: массив слогов слова (list of Syllable)
        """
        syllables = []
        begin = 0
        number = 0
        for i in range(len(word)):
            if word[i] in VOWELS:
                if i+1 < len(word)-1 and word[i+1] in CLOSED_SYLLABLE_CHARS:
                    if i+2 < len(word)-1 and word[i+2] in "ьЬ":
                        # Если после закрывающего согласного идёт мягкий знак, заканчиваем на нём. ("бань-ка")
                        end = i+3
                    elif i+2 < len(word)-1 and word[i+2] not in VOWELS and word[i+1] != word[i+2]:
                        # Если после закрывающего согласного не идёт гласная или такая же согласная,
                        # слог закрывается на этой согласной. ("май-ка")
                        end = i+2
                    else:
                        # Несмотря на наличие закрывающего согласного, заканчиваем на гласной. ("со-ло", "да-нный")
                        end = i+1
                else:
                    # Если после гласной идёт не закрывающая согласная, заканчиваем на гласной. ("ко-гда")
                    end = i+1
                syllables.append(Syllable(begin, end, number, word[begin:end]))
                number += 1
                begin = end
        if get_first_vowel_position(word) != -1:
            # Добиваем последний слог до конца слова.
            syllables[-1] = Syllable(syllables[-1].begin, len(word), syllables[-1].number,
                                     word[syllables[-1].begin:len(word)])
        return syllables

    @staticmethod
    def get_word_accent(word, accents_dict):
        """
        Определение ударения в слове по словарю. Возможно несколько вариантов ударения.

        :param word: слово для простановки ударений
        :param accents_dict: экземпляр обёртки для словаря ударений
        :return accents: массив позиций букв, на которые падает ударение
        """
        accents = []
        if count_vowels(word) == 0:
            # Если гласных нет, то и ударений нет.
            pass
        elif count_vowels(word) == 1:
            # Если одна гласная, то на неё и падает ударение.
            accents.append(get_first_vowel_position(word))
        elif word.find("ё") != -1:
            # Если есть буква "ё", то только на неё может падать ударение.
            accents.append(word.find("ё"))
        else:
            # Проверяем словарь на наличие форм с ударениями.
            forms = accents_dict.data.get(word)
            if forms is not None:
                accents = list(set([form.find("'") - 1 for form in forms if form.find("'") != -1]))
            if 'е' in word:
                # Находим все возможные варинаты преобразований 'е' в 'ё'.
                positions = [i for i in range(len(word)) if word[i] == 'е']
                beam = [word[:positions[0]]]
                for i in range(len(positions)):
                    new_beam = []
                    for prefix in beam:
                        n = positions[i+1] if i+1 < len(positions) else len(word)
                        new_beam.append(prefix + 'ё' + word[positions[i]+1:n])
                        new_beam.append(prefix + 'е' + word[positions[i]+1:n])
                        beam = new_beam
                # И проверяем их по словарю.
                for permutation in beam:
                    if accents_dict.data.get(permutation) is not None:
                        yo_pos = permutation.find("ё")
                        if yo_pos != -1:
                            accents.append(yo_pos)
        return accents

    @staticmethod
    def get_word_transcription(word):
        """
        Фонетическая транскрипция слова на основе упорядоченного набора правил вида A->B,
        где A и B - последовательности символов.

        :param word: слово для разбора
        :return phonetics: фонетическое слово
        """
        # TODO: Составление набора правил.
        ruleset = {

        }

    @staticmethod
    def get_rhyme_profile(word):
        """
        Получение профиля рифмовки (набора признаков для сопоставления)

        :param word: уже акцентуированное слово (Word)
        :return profile: профиль рифмовки
        """
        # TODO: Переход на фонетическое слово, больше признаков.
        accented_char = ''
        count_syllable = 0
        prev_char = ''
        next_char = ''
        for syllable in reversed(word.syllables):
            count_syllable += 1
            if syllable.accent != -1:
                accented_char = word.text[syllable.accent]
                if syllable.accent-1 >= 0:
                    prev_char = word.text[syllable.accent-1]
                if syllable.accent+1 < len(word.text):
                    next_char = word.text[syllable.accent+1]
                break
        return accented_char, count_syllable, next_char, prev_char

    @staticmethod
    def is_rhyme(word1, word2):
        """
        Проверка рифмованности 2 слов.

        :param word1: первое слово для проверки рифмы, уже акцентуированное (Word)
        :param word2: второе слово для проверки рифмы, уже акцентуированное (Word)
        :return result: является рифмой или нет
        """
        features1 = Phonetics.get_rhyme_profile(word1)
        features2 = Phonetics.get_rhyme_profile(word2)
        count_equality = 0
        for i in range(len(features1)):
            if features1[i] == features2[i]:
                count_equality += 1
        return count_equality >= 3 and features1[0] == features2[0] and features1[1] == features2[1]

    @staticmethod
    def get_all_rhymes(markup, short_words):
        """
        Получение всех рифм в разметке

        :param markup: разметка
        :param short_words: сопоставление коротких версии слов в разметке с нормальными версиями.
        :return result: словарь всех рифм
        """
        rhymes = {}
        rhyme_candidates = []
        for line in markup.lines:
            if len(line.words) != 0:
                rhyme_candidates.append(line.words[-1])
        for i in range(len(rhyme_candidates)):
            for j in range(i+1, len(rhyme_candidates)):
                words = (rhyme_candidates[i], rhyme_candidates[j])
                if Phonetics.is_rhyme(words[0], words[1]):
                    shorts = (words[0].get_short(), words[1].get_short())
                    short_words[shorts[0]] = words[0]
                    short_words[shorts[1]] = words[1]
                    for item in [shorts, tuple(reversed(shorts))]:
                        if rhymes.get(item[0]) is None:
                            rhymes[item[0]] = dict()
                        if rhymes[item[0]].get(item[1]) is None:
                            rhymes[item[0]][item[1]] = 0
                        rhymes[item[0]][item[1]] += 1
        return rhymes

    @staticmethod
    def process_text(text, accents_dict):
        """
        Получение начального варианта разметки по слогам и ударениям.

        :param text: текст для разметки
        :param accents_dict: экземпляр обёртки для словаря ударений
        :return markup: разметка по слогам и ударениям
        """
        begin_word = -1
        begin_line = 0
        lines = []
        words = []
        # TODO: Нормальная токенизация.
        for i in range(len(text)):
            valid_word_symbol = text[i].isalpha() and i != len(text) - 1
            if valid_word_symbol and begin_word == -1:
                begin_word = i
            if not valid_word_symbol and begin_word != -1:
                # Каждое слово разбиваем на слоги.
                word = Word(begin_word, i, text[begin_word:i], Phonetics.get_word_syllables(text[begin_word:i]))
                # Проставляем ударения.
                accents = Phonetics.get_word_accent(word.text.lower(), accents_dict)
                # Сопоставляем ударения слогам.
                for syllable in word.syllables:
                    for accent in accents:
                        if syllable.begin <= accent < syllable.end:
                            syllable.accent = accent
                words.append(word)
                begin_word = -1
            if text[i] == "\n":
                # Разбиваем по строкам.
                lines.append(Line(begin_line, i+1, text[begin_line:i], words))
                words = []
                begin_line = i+1
        if begin_line != len(text):
            lines.append(Line(begin_line, len(text), text[begin_line:len(text)], words))
        return Markup(text, lines)
