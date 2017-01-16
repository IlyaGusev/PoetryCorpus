# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Классификатор метра.

from poetry.apps.corpus.scripts.preprocess import get_first_vowel_position


class MetreClassifier:
    """
    Классификатор, считает отклонения от стандартных шаблонов ритма(метров),
    у какого метра меньше оишбок, тот и выбираем.
    """
    def __init__(self, markup, accent_clf=None):
        """
        :param markup: разметка по слогам и ударениям
        :param accent_clf: классификатор ударений, если хотим использовать
        """
        self.markup = markup
        self.accent_classifier = accent_clf
        self.metres = {
            "iambos": '-+',
            "choreios": '+-',
            "daktylos": '+--',
            "amphibrachys": '-+-',
            "anapaistos": '--+',
        }
        self.result_metre = None
        self.errors_count = {k: 0 for k in self.metres.keys()}
        self.corrected_accents = {k: [] for k in self.metres.keys()}
        self.omograph_resolutions = {k: [] for k in self.metres.keys()}
        self.additions = {k: [] for k in self.metres.keys()}
        self.after_ml = []

    def classify_metre(self):
        """
        Классифицируем стихотворный метр.
        Правило 1: Ударения МОГУТ падать только на икты соответствующей метрической схемы,
        если только эти ударения не подпадают под Исключение 1.
        Исключение 1: Ударения могут приходиться на слабое место,
        если безударный слог ТОГО ЖЕ слова не попадает на икт.

        :return: лучший метр и его ошибки и исправления
        """
        # TODO: Дольник и тактовик, цезура и другие эффекты.
        # TODO: Рефакторинг.
        for l in range(len(self.markup.lines)):
            line = self.markup.lines[l]
            for metre_name, metre_pattern in self.metres.items():
                pattern = ""
                syllables_count = sum([len(word.syllables) for word in line.words])
                while len(pattern) < syllables_count:
                    pattern += metre_pattern
                syllable_number = 0
                for w in range(len(line.words)):
                    word = line.words[w]
                    accents_count = sum([1 for syllable in word.syllables if syllable.accent != -1])
                    found_error = False
                    for syllable in word.syllables:
                        if accents_count >= 1 and pattern[syllable_number] == "-" and syllable.accent != -1:
                            for other_syllable in word.syllables:
                                other_syllable_number = other_syllable.number - syllable.number + syllable_number
                                if syllable.number != other_syllable.number and pattern[other_syllable_number] == "+":
                                    if not found_error:
                                        self.errors_count[metre_name] += 1
                                        found_error = True
                                    correction = {'line_number': l, 'word_number': w,
                                                  'syllable_number': other_syllable.number,
                                                  'word_text': word.text}
                                    if accents_count == 1:
                                        self.corrected_accents[metre_name].append(correction)
                                    else:
                                        self.omograph_resolutions[metre_name].append(correction)
                        if accents_count == 0:
                            if pattern[syllable_number] == "+":
                                addition = {'line_number': l, 'word_number': w,
                                            'syllable_number': syllable.number,
                                            'word_text': word.text}
                                self.additions[metre_name].append(addition)
                        syllable_number += 1
        self.result_metre = min(self.errors_count, key=self.errors_count.get)
        return self.result_metre

    def get_ml_results(self):
        if self.accent_classifier is not None:
            result_additions = self.additions[self.result_metre]
            for i in range(len(result_additions)):
                for j in range(i, len(result_additions)):
                    text1 = result_additions[i]['word_text']
                    text2 = result_additions[j]['word_text']
                    number1 = result_additions[i]['syllable_number']
                    number2 = result_additions[j]['syllable_number']
                    if text1 == text2 and number1 != number2:
                        accent = self.accent_classifier.classify_accent([text1, ])
                        if accent[0] == number1:
                            self.after_ml.append(result_additions[i])
                        if accent[0] == number2:
                            self.after_ml.append(result_additions[j])
        return self.after_ml

    def get_improved_markup(self):
        """
        Улучшаем разметку после классификации метра.

        :return: markup: улучшенная по метру разметка
        """
        for pos in self.corrected_accents[self.result_metre] + self.omograph_resolutions[self.result_metre]:
            syllables = self.markup.lines[pos['line_number']].words[pos['word_number']].syllables
            for i in range(len(syllables)):
                syllable = syllables[i]
                syllable.accent = -1
                if syllable.number == pos['syllable_number']:
                    syllable.accent = syllable.begin + get_first_vowel_position(syllable.text)

        for pos in self.additions[self.result_metre]:
            syllable = self.markup.lines[pos['line_number']].words[pos['word_number']].syllables[pos['syllable_number']]
            syllable.accent = syllable.begin + get_first_vowel_position(syllable.text)

        for pos in self.after_ml:
            syllables = self.markup.lines[pos['line_number']].words[pos['word_number']].syllables
            for i in range(len(syllables)):
                syllable = syllables[i]
                syllable.accent = -1
                if syllable.number == pos['syllable_number']:
                    syllable.accent = syllable.begin + get_first_vowel_position(syllable.text)
        return self.markup
