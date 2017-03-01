# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Классификатор метра.

import json
from collections import OrderedDict
from poetry.apps.corpus.scripts.preprocess import get_first_vowel_position
from poetry.apps.corpus.scripts.metre.patterns import Patterns
from poetry.apps.corpus.scripts.phonetics.phonetics_markup import CommonMixin


class ErrorCorrection(CommonMixin):
    def __init__(self, line_number, word_number, syllable_number, word_text, accent):
        self.line_number = line_number
        self.word_number = word_number
        self.syllable_number = syllable_number
        self.word_text = word_text
        self.accent = accent


class ClassificationResult(CommonMixin):
    """
    Результат классификации по метру.
    """
    def __init__(self, count_lines=0):
        self.metre = None
        self.pattern = None
        self.line_metres = [ClassificationResult(0) for i in range(count_lines)]
        self.errors_count = {k: 0 for k in MetreClassifier.metres.keys()}
        self.corrections = {k: [] for k in MetreClassifier.metres.keys()}
        self.resolutions = {k: [] for k in MetreClassifier.metres.keys()}
        self.additions = {k: [] for k in MetreClassifier.metres.keys()}
        self.ml_resolutions = []

    def get_metre_errors_count(self):
        return self.errors_count[self.metre]

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def from_json(self, st):
        self.__dict__.update(json.loads(st))
        return self

    def __str__(self):
        st = "Метр: " + str(self.metre) + "\n"
        st += "Снятая омография: \n" + "\n".join(
            [str((item['word_text'], item['syllable_number'])) for item in self.resolutions[self.metre]]) + "\n"
        st += "Неправильные ударения: \n" + "\n".join(
            [str((item['word_text'], item['syllable_number'])) for item in self.corrections[self.metre]]) + "\n"
        st += "Новые ударения: \n" + "\n".join(
            [str((item['word_text'], item['syllable_number'])) for item in self.additions[self.metre]]) + "\n"
        st += "ML: \n" + "\n".join(
            [str((item['word_text'], item['syllable_number'])) for item in self.ml_resolutions]) + "\n"
        return st


class MetreClassifier(object):
    """
    Классификатор, считает отклонения от стандартных шаблонов ритма(метров),
    у какого метра меньше оишбок, тот и выбираем.
    """
    metres = OrderedDict(
        [("iambos", '(us)*(uS)(U)?(U)?'),
         ("choreios", '(su)*(S)(U)?(U)?'),
         ("daktylos", '(suu)*(S)(U)?(U)?'),
         ("amphibrachys", '(usu)*(uS)(U)?(U)?'),
         ("anapaistos",  '(uus)*(uuS)(U)?(U)?'),
         ("dolnik3", '(U)?(U)?((su)(u)?)*(S)(U)?(U)?'),
         ("dolnik2", '(U)?(U)?((s)(u)?)*(S)(U)?(U)?'),
         ("taktovik3", '(U)?(U)?((Su)(u)?(u)?)*(S)(U)?(U)?'),
         ("taktovik2", '(U)?(U)?((S)(u)?(u)?)*(S)(U)?(U)?')])

    coef = OrderedDict(
        [("iambos", 1.0),
         ("choreios", 1.0),
         ("daktylos", 1.0),
         ("amphibrachys", 1.0),
         ("anapaistos",  1.0),
         ("dolnik3", 0.9),
         ("dolnik2", 0.9),
         ("taktovik3", 0.7),
         ("taktovik2", 0.7)])

    border_syllables_count = 18

    compilations = {metre_name: [None for i in range(1, 25)] for metre_name, expression in metres.items()}

    @staticmethod
    def classify_metre(markup):
        """
        Классифицируем стихотворный метр.
        :param markup: разметка.
        :return: результат классификации.
        """
        result = ClassificationResult(len(markup.lines))
        for metre_name, metre_pattern in MetreClassifier.metres.items():
            for l in range(len(markup.lines)):
                line = markup.lines[l]
                line_syllables = sum([len(word.syllables) for word in line.words])

                # Строчки длиной больше border_syllables_count слогов не обрабатываем.
                if line_syllables > MetreClassifier.border_syllables_count:
                    continue
                # Используем запомненные шаблоны, если их нет - компилируем и запоминаем.
                patterns = MetreClassifier.compilations[metre_name][line_syllables]
                if patterns is None:
                    MetreClassifier.compilations[metre_name][line_syllables] = \
                        Patterns.compile_pattern(metre_pattern, line_syllables)
                patterns = MetreClassifier.compilations[metre_name][line_syllables]
                patterns = [pattern.lower() for pattern in patterns]

                # Выбираем лучший шаблон для данной строчки.
                minimum_error_count = 100
                if len(patterns) == 0:
                    continue
                for pattern in patterns:
                    error_count, corrections, resolutions, additions = \
                        MetreClassifier.line_pattern_matching(line, l, pattern)
                    if error_count < minimum_error_count:
                        minimum_error_count = error_count
                        result.line_metres[l].errors_count[metre_name] = minimum_error_count
                        result.line_metres[l].corrections[metre_name] = corrections
                        result.line_metres[l].resolutions[metre_name] = resolutions
                        result.line_metres[l].additions[metre_name] = additions

        # Считаем лучший метр для каждой строки.
        line_metres = [[] for i in range(len(markup.lines))]
        for l in range(len(markup.lines)):
            minimum_error_count = 100
            for metre_name in MetreClassifier.metres.keys():
                error_count = result.line_metres[l].errors_count[metre_name]
                if error_count < minimum_error_count:
                    minimum_error_count = error_count
            for metre_name in MetreClassifier.metres.keys():
                error_count = result.line_metres[l].errors_count[metre_name]
                if error_count == minimum_error_count:
                    line_metres[l].append(metre_name)
        # Выбираем общий метр по метрам строк с учётом коэффициентов.
        counter = {k: 0 for k in MetreClassifier.metres.keys()}
        for l in range(len(markup.lines)):
            for metre in line_metres[l]:
                counter[metre] += 1
        for key in counter.keys():
            counter[key] *= MetreClassifier.coef[key]
        result.metre = max(counter, key=counter.get)
        for l in range(len(markup.lines)):
            result.corrections[result.metre] += result.line_metres[l].corrections[result.metre]
            result.resolutions[result.metre] += result.line_metres[l].resolutions[result.metre]
            result.additions[result.metre] += result.line_metres[l].additions[result.metre]
            result.errors_count[result.metre] += result.line_metres[l].errors_count[result.metre]
        return result

    @staticmethod
    def line_pattern_matching(line, line_number, pattern):
        """
        Ударения могут приходиться на слабое место,
        если безударный слог того же слова не попадает на икт.
        :param line: строка.
        :param line_number: номер строки.
        :param pattern: шаблон.
        :return: количество ошибок и сами ошибки, дополнения и снятия
        """
        corrections = []
        resolutions = []
        additions = []
        number_in_pattern = 0
        for w in range(len(line.words)):
            word = line.words[w]
            if len(word.syllables) <= 1:
                number_in_pattern += len(word.syllables)
                continue
            accents_count = sum([1 for syllable in word.syllables if syllable.accent != -1])
            for syllable in word.syllables:
                if accents_count >= 1 and pattern[number_in_pattern] == "u" and syllable.accent != -1:
                    for other_syllable in word.syllables:
                        if syllable.number == other_syllable.number:
                            continue
                        other_number_in_pattern = other_syllable.number - syllable.number + number_in_pattern
                        if pattern[other_number_in_pattern] == "s":
                            accent = get_first_vowel_position(other_syllable.text) + other_syllable.begin
                            correction = ErrorCorrection(line_number, w, other_syllable.number, word.text, accent)
                            if accents_count == 1 and other_syllable.accent == -1:
                                corrections.append(correction)
                            else:
                                resolutions.append(correction)
                if accents_count == 0:
                    if pattern[number_in_pattern] == "s":
                        accent = get_first_vowel_position(syllable.text) + syllable.begin
                        addition = ErrorCorrection(line_number, w, syllable.number, word.text, accent)
                        additions.append(addition)
                number_in_pattern += 1
        return len(corrections), corrections, resolutions, additions

    @staticmethod
    def get_ml_resolutions(result, accent_classifier):
        """
        Пытаемся снять омонимию с предыдущих этапов древесным классификатором.
        :param result: результат классификации.
        :param accent_classifier: древесный классификатор ударений.
        :return: улучшенный результат.
        """
        result_additions = result.additions[result.metre]
        for i in range(len(result_additions)):
            for j in range(i, len(result_additions)):
                text1 = result_additions[i].word_text
                text2 = result_additions[j].word_text
                number1 = result_additions[i].syllable_number
                number2 = result_additions[j].syllable_number
                if text1 == text2 and number1 != number2:
                    accent = accent_classifier.classify_accent(text1)
                    if accent == number1:
                        result.ml_resolutions.append(result_additions[i])
                    if accent == number2:
                        result.ml_resolutions.append(result_additions[j])
        return result

    @staticmethod
    def get_improved_markup(markup, result):
        """
        Улучшаем разметку после классификации метра.
        :param markup: начальная разметка.
        :param result: результат классификации.
        :return: улучшенная разметка.
        """
        for pos in result.corrections[result.metre] + result.resolutions[result.metre]:
            syllables = markup.lines[pos.line_number].words[pos.word_number].syllables
            for i in range(len(syllables)):
                syllable = syllables[i]
                syllable.accent = -1
                if syllable.number == pos.syllable_number:
                    syllable.accent = syllable.begin + get_first_vowel_position(syllable.text)

        for pos in result.additions[result.metre]:
            syllable = markup.lines[pos.line_number].words[pos.word_number].syllables[pos.syllable_number]
            syllable.accent = syllable.begin + get_first_vowel_position(syllable.text)

        for pos in result.ml_resolutions:
            syllables = markup.lines[pos.line_number].words[pos.word_number].syllables
            for i in range(len(syllables)):
                syllable = syllables[i]
                syllable.accent = -1
                if syllable.number == pos.syllable_number:
                    syllable.accent = syllable.begin + get_first_vowel_position(syllable.text)
        return markup

    @staticmethod
    def improve_markup(markup, accents_classifier=None):
        """
        Улучшение разметки метрическим и машинным классификатором.
        :param markup: начальная разметка.
        :param accents_classifier: классификатор ударений.
        """
        result = MetreClassifier.classify_metre(markup)
        if accents_classifier is not None:
            result = MetreClassifier.get_ml_resolutions(result, accents_classifier)
        return MetreClassifier.get_improved_markup(markup, result), result