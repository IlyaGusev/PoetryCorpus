# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Классификатор метра.

import json
from poetry.apps.corpus.scripts.preprocess import get_first_vowel_position


class ClassificationResult(object):
    """
    Результат классификации по метру.
    """
    def __init__(self):
        self.metre = None
        self.errors_count = {k: 0 for k in MetreClassifier.metres.keys()}
        self.corrections = {k: [] for k in MetreClassifier.metres.keys()}
        self.resolutions = {k: [] for k in MetreClassifier.metres.keys()}
        self.additions = {k: [] for k in MetreClassifier.metres.keys()}
        self.ml_resolutions = []

    def get_metre_errors_count(self):
        return self.errors_count[self.metre]

    def to_json(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

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
    metres = {
        "iambos": '-+',
        "choreios": '+-',
        "daktylos": '+--',
        "amphibrachys": '-+-',
        "anapaistos": '--+',
    }

    @staticmethod
    def classify_metre(markup):
        """
        Классифицируем стихотворный метр.
        Правило 1: Ударения МОГУТ падать только на икты соответствующей метрической схемы,
        если только эти ударения не подпадают под Исключение 1.
        Исключение 1: Ударения могут приходиться на слабое место,
        если безударный слог ТОГО ЖЕ слова не попадает на икт.
        :param markup: разметка.
        :return: результат классификации.
        """
        # TODO: Дольник и тактовик, цезура и другие эффекты.
        result = ClassificationResult()
        for metre_name, metre_pattern in MetreClassifier.metres.items():
            for l in range(len(markup.lines)):
                line = markup.lines[l]
                pattern = MetreClassifier.extend_pattern(metre_pattern, line)
                number_in_pattern = 0
                for w in range(len(line.words)):
                    word = line.words[w]
                    if len(word.syllables) <= 1:
                        number_in_pattern += len(word.syllables)
                        continue
                    accents_count = sum([1 for syllable in word.syllables if syllable.accent != -1])
                    for syllable in word.syllables:
                        if accents_count >= 1 and pattern[number_in_pattern] == "-" and syllable.accent != -1:
                            for other_syllable in word.syllables:
                                if syllable.number == other_syllable.number:
                                    continue
                                other_number_in_pattern = other_syllable.number - syllable.number + number_in_pattern
                                if pattern[other_number_in_pattern] == "+":
                                    accent = get_first_vowel_position(other_syllable.text) + other_syllable.begin
                                    correction = {'line_number': l, 'word_number': w,
                                                  'syllable_number': other_syllable.number,
                                                  'word_text': word.text, 'accent': accent}
                                    if accents_count == 1 and other_syllable.accent == -1:
                                        result.corrections[metre_name].append(correction)
                                    else:
                                        result.resolutions[metre_name].append(correction)
                        if accents_count == 0:
                            if pattern[number_in_pattern] == "+":
                                accent = get_first_vowel_position(syllable.text) + syllable.begin
                                addition = {'line_number': l, 'word_number': w,
                                            'syllable_number': syllable.number,
                                            'word_text': word.text, 'accent': accent}
                                result.additions[metre_name].append(addition)
                        number_in_pattern += 1

        for metre_name in MetreClassifier.metres.keys():
            result.errors_count[metre_name] = \
                len(set([correction['word_text'] for correction in result.corrections[metre_name]]))
        result.metre = min(result.errors_count, key=result.errors_count.get)
        return result

    @staticmethod
    def extend_pattern(metre_pattern, line):
        """
        Расширение шаблона до конца строки.
        :param metre_pattern: шаблон метра.
        :param line: строка (Line).
        :return: шаблон на всю строку.
        """
        pattern = ""
        syllables_count = sum([len(word.syllables) for word in line.words])
        while len(pattern) < syllables_count:
            pattern += metre_pattern
        return pattern

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
                text1 = result_additions[i]['word_text']
                text2 = result_additions[j]['word_text']
                number1 = result_additions[i]['syllable_number']
                number2 = result_additions[j]['syllable_number']
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
            syllables = markup.lines[pos['line_number']].words[pos['word_number']].syllables
            for i in range(len(syllables)):
                syllable = syllables[i]
                syllable.accent = -1
                if syllable.number == pos['syllable_number']:
                    syllable.accent = syllable.begin + get_first_vowel_position(syllable.text)

        for pos in result.additions[result.metre]:
            syllable = markup.lines[pos['line_number']].words[pos['word_number']].syllables[pos['syllable_number']]
            syllable.accent = syllable.begin + get_first_vowel_position(syllable.text)

        for pos in result.ml_resolutions:
            syllables = markup.lines[pos['line_number']].words[pos['word_number']].syllables
            for i in range(len(syllables)):
                syllable = syllables[i]
                syllable.accent = -1
                if syllable.number == pos['syllable_number']:
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
