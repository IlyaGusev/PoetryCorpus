# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Классификатор метра.

from collections import OrderedDict, Counter
from typing import List, Dict, Tuple
import jsonpickle

from poetry.apps.corpus.scripts.main.markup import Line, Markup
from poetry.apps.corpus.scripts.util.mixins import CommonMixin
from poetry.apps.corpus.scripts.metre.patterns import CompiledPatterns
from poetry.apps.corpus.scripts.util.preprocess import get_first_vowel_position
from poetry.apps.corpus.scripts.accents.classifier import MLAccentClassifier


class AccentCorrection(CommonMixin):
    """
    Исправление ударения.
    """
    def __init__(self, line_number: int, word_number: int, syllable_number: int,
                 word_text: str, accent: int) -> None:
        """
        :param line_number: номер строки.
        :param word_number: номер слова.
        :param syllable_number: номер слога.
        :param word_text: текст слова.
        :param accent: позиция ударения (с 0).
        """
        self.line_number = line_number
        self.word_number = word_number
        self.syllable_number = syllable_number
        self.word_text = word_text
        self.accent = accent


class LineClassificationResult(CommonMixin):
    """
    Результат классификации строки.
    """
    def __init__(self) -> None:
        self.error_count = {metre_name: Counter() for metre_name in MetreClassifier.metres.keys()}

    def store_pattern_result(self, metre_name: str, pattern: str, error_count: int) -> None:
        """
        Сохранить результат сравнения строки с шаблоном метра.

        :param metre_name: имя метра.
        :param pattern: шаблон метра.
        :param error_count: количество ошибок.
        """
        self.error_count[metre_name][pattern] = error_count

    def get_best_patterns(self) -> Dict[str, str]:
        """
        :return: лучшие шаблоны каждого метра.
        """
        patterns = {}  # type: Dict[str, str]
        for metre_name in MetreClassifier.metres.keys():
            patterns[metre_name] = min(self.error_count[metre_name], key=self.error_count[metre_name].get, default="")
        return patterns

    def get_best_metres(self) -> List[str]:
        """
        :return: метры с наименьшим количеством ошибок.
        """
        metre_errors_counter = Counter(MetreClassifier.metres.keys())
        for metre_name, pattern in self.get_best_patterns().items():
            metre_errors_counter[metre_name] = self.error_count[metre_name][pattern]
        min_errors = metre_errors_counter[min(metre_errors_counter, key=metre_errors_counter.get)]
        result_metres = []
        for key, value in metre_errors_counter.items():
            if value == min_errors:
                result_metres.append(key)
        return result_metres


class ClassificationResult(CommonMixin):
    """
    Результат классификации стихотворения по метру.
    """
    def __init__(self, count_lines: int=0) -> None:
        """
        :param count_lines: количество строк.
        """
        self.metre = None
        self.count_lines = count_lines
        self.lines_result = [LineClassificationResult() for i in range(count_lines)]
        self.errors_count = {k: 0 for k in MetreClassifier.metres.keys()}  # type: Dict[str, int]
        self.corrections = {k: [] for k in MetreClassifier.metres.keys()}  # type: Dict[str, List[AccentCorrection]]
        self.resolutions = {k: [] for k in MetreClassifier.metres.keys()}  # type: Dict[str, List[AccentCorrection]]
        self.additions = {k: [] for k in MetreClassifier.metres.keys()}  # type: Dict[str, List[AccentCorrection]]
        self.ml_resolutions = []  # type: List[AccentCorrection]

    def get_metre_errors_count(self):
        """
        :return: получить количество ошибок на заданном метре.
        """
        return self.errors_count[self.metre]

    def to_json(self):
        """
        :return: сериализация в json.
        """
        return jsonpickle.encode(self)

    @staticmethod
    def str_corrections(collection: List[AccentCorrection]) -> str:
        """
        :param collection: список исправлений.
        :return: его строковое представление.
        """
        return"\n".join([str((item.word_text, item.syllable_number)) for item in collection])

    def __str__(self):
        st = "Метр: " + str(self.metre) + "\n"
        st += "Снятая омография: \n" + ClassificationResult.str_corrections(self.resolutions[self.metre]) + "\n"
        st += "Неправильные ударения: \n" + ClassificationResult.str_corrections(self.corrections[self.metre]) + "\n"
        st += "Новые ударения: \n" + ClassificationResult.str_corrections(self.additions[self.metre]) + "\n"
        st += "ML: \n" + ClassificationResult.str_corrections(self.ml_resolutions) + "\n"
        return st


class MetreClassifier(object):
    """
    Классификатор, считает отклонения от стандартных шаблонов ритма(метров).
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
    compilations = CompiledPatterns()

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
                line_syllables_count = sum([len(word.syllables) for word in line.words])

                # Строчки длиной больше border_syllables_count слогов не обрабатываем.
                if line_syllables_count > MetreClassifier.border_syllables_count:
                    continue
                # Используем запомненные шаблоны, если их нет - компилируем и запоминаем.
                patterns = MetreClassifier.compilations.get_patterns(metre_name, metre_pattern, line_syllables_count)
                patterns = [pattern.lower() for pattern in patterns]

                # Сохраняем результаты по всем шаблонам.
                if len(patterns) == 0:
                    continue
                for pattern in patterns:
                    if pattern == "":
                        continue
                    error_count, corrections, resolutions, additions = \
                        MetreClassifier.line_pattern_matching(line, l, pattern)
                    result.lines_result[l].store_pattern_result(metre_name, pattern, error_count)

        # Считаем лучшие метры для каждой строки.
        line_metres = [result.lines_result[i].get_best_metres() for i in range(len(markup.lines))]

        # Выбираем общий метр по метрам строк с учётом коэффициентов.
        counter = {k: 0 for k in MetreClassifier.metres.keys()}
        for l in range(len(markup.lines)):
            for metre in line_metres[l]:
                counter[metre] += 1
        for key in counter.keys():
            counter[key] *= MetreClassifier.coef[key]
        result.metre = max(counter, key=counter.get)

        # Запомним все исправления.
        for l in range(len(markup.lines)):
            pattern = result.lines_result[l].get_best_patterns()[result.metre]
            if pattern == "":
                continue
            error_count, corrections, resolutions, additions =\
                MetreClassifier.line_pattern_matching(markup.lines[l], l, pattern)
            result.corrections[result.metre] += corrections
            result.resolutions[result.metre] += resolutions
            result.additions[result.metre] += additions
            result.errors_count[result.metre] += error_count
        return result

    @staticmethod
    def line_pattern_matching(line: Line, line_number: int, pattern: str) -> \
            Tuple[int, List[AccentCorrection], List[AccentCorrection], List[AccentCorrection]]:
        """
        Ударения могут приходиться на слабое место,
        если безударный слог того же слова не попадает на икт. Иначе - ошибка.

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
            # Игнорируем слова длиной меньше 2 слогов.
            if len(word.syllables) <= 1:
                number_in_pattern += len(word.syllables)
                continue
            accents_count = word.count_accents()
            for syllable in word.syllables:
                if accents_count == 0 and pattern[number_in_pattern] == "s":
                    # Ударений нет, ставим такое, какое подходит по метру. Возможно несколько.
                    additions.append(AccentCorrection(line_number, w, syllable.number, word.text, syllable.vowel()))
                elif pattern[number_in_pattern] == "u" and syllable.accent != -1:
                    # Ударение есть и оно падает на этот слог, при этом в шаблоне безударная позиция.
                    # Найдём такой слог, у которого в шаблоне ударная позиция. Это и есть наше исправление.
                    for other_syllable in word.syllables:
                        other_number_in_pattern = other_syllable.number - syllable.number + number_in_pattern
                        if syllable.number == other_syllable.number or pattern[other_number_in_pattern] != "s":
                            continue
                        ac = AccentCorrection(line_number, w, other_syllable.number, word.text, other_syllable.vowel())
                        if accents_count == 1 and other_syllable.accent == -1:
                            corrections.append(ac)
                        else:
                            resolutions.append(ac)
                number_in_pattern += 1
        return len(corrections), corrections, resolutions, additions

    @staticmethod
    def get_ml_resolutions(result: ClassificationResult, accent_classifier: MLAccentClassifier) -> None:
        """
        Пытаемся снять омонимию с предыдущих этапов древесным классификатором.

        :param result: результат классификации.
        :param accent_classifier: древесный классификатор ударений.
        """
        result_additions = result.additions[result.metre]  # type: List[AccentCorrection]
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

    @staticmethod
    def get_improved_markup(markup: Markup, result: ClassificationResult) -> Markup:
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
    def improve_markup(markup: Markup, accents_classifier: MLAccentClassifier=None) -> Markup:
        """
        Улучшение разметки метрическим и машинным классификатором.

        :param markup: начальная разметка.
        :param accents_classifier: классификатор ударений.
        """
        result = MetreClassifier.classify_metre(markup)
        if accents_classifier is not None:
            MetreClassifier.get_ml_resolutions(result, accents_classifier)
        return MetreClassifier.get_improved_markup(markup, result), result
