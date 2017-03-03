# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Модуль для описания разметки по ударениям и слогам.

import xml.etree.ElementTree as etree
from dicttoxml import dicttoxml
import json

from poetry.apps.corpus.scripts.preprocess import get_first_vowel_position


def to_dict(obj):
    """
    Преобразование объекта в словарь.
    :param obj: объект, который нужно превратить в словарь
    :return data: получившийся словарь
    """
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = to_dict(v)
        return data
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [to_dict(v) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, to_dict(value)) for key, value in obj.__dict__.items()
                    if not callable(value) and not key.startswith('_')])
        return data
    else:
        return obj


class CommonMixin(object):
    """
    Mixin для удобного сравнения и преобразования в dict разметок.
    """
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self):
        return str(self.to_dict())

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self):
        return to_dict(self)


class Syllable(CommonMixin):
    """
    Класс данных для слогов.
    """
    def __init__(self, begin, end, number, text, accent=-1):
        self.begin = begin
        self.end = end
        self.number = number
        self.text = text
        self.accent = accent

    def vowel(self):
        return get_first_vowel_position(self.text) + self.begin

    def from_dict(self, d):
        self.__dict__.update(d)
        return self


class Word(CommonMixin):
    """
    Класс данных для слов.
    """
    def __init__(self, begin, end, text, syllables):
        self.begin = begin
        self.end = end
        self.text = text
        self.syllables = syllables

    def count_accents(self):
        return sum(syllable.accent != -1 for syllable in self.syllables)

    def accent(self):
        accent = -1
        for syllable in self.syllables:
            if syllable.accent != -1:
                accent = syllable.accent
        return accent

    def get_short(self):
        return self.text.lower() + str(self.accent())

    def __hash__(self):
        return hash(self.get_short())

    def from_dict(self, d):
        self.__dict__.update(d)
        syllables = [Syllable(0, 0, 0, "") for syllable in self.syllables]
        self.syllables = [syllables[i].from_dict(self.syllables[i]) for i in range(len(syllables))]
        return self


class Line(CommonMixin):
    """
    Класс данных для строк.
    """
    def __init__(self, begin, end, text, words):
        self.begin = begin
        self.end = end
        self.text = text
        self.words = words

    def from_dict(self, d):
        self.__dict__.update(d)
        words = [Word(0, 0, "", []) for word in self.words]
        self.words = [words[i].from_dict(self.words[i]) for i in range(len(words))]
        return self


class Markup(CommonMixin):
    """
    Класс данных для разметки в целом с экспортом/импортом в XML и JSON.
    """
    def __init__(self, text=None, lines=None):
        # TODO: При изменении структуры разметки менять десериализацию.
        self.text = text
        self.lines = lines
        self.version = 2

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def from_json(self, st):
        d = json.loads(st)
        self.__dict__.update(d)
        lines = [Line(0, 0, "", []) for line in self.lines]
        self.lines = [lines[i].from_dict(self.lines[i]) for i in range(len(lines))]
        return self

    def to_xml(self):
        """
        Экспорт в XML.
        :return self: строка в формате XML
        """
        return dicttoxml(self.to_dict(), custom_root='markup', attr_type=False).decode('utf-8')

    def from_xml(self, xml):
        """
        Импорт из XML.
        :param xml: XML-разметка
        :return self: получившийся объект Markup
        """
        root = etree.fromstring(xml)
        if root.find("version") is None or int(root.find("version").text) != self.version:
            return None
        lines_node = root.find("lines")
        lines = []
        for line_node in lines_node.findall("item"):
            words_node = line_node.find("words")
            words = []
            for word_node in words_node.findall("item"):
                syllables_node = word_node.find("syllables")
                syllables = []
                for syllable_node in syllables_node.findall("item"):
                    syllables.append(Syllable(int(syllable_node.find("begin").text),
                                              int(syllable_node.find("end").text),
                                              int(syllable_node.find("number").text),
                                              syllable_node.find("text").text,
                                              int(syllable_node.find("accent").text)))
                words.append(Word(int(word_node.find("begin").text), int(word_node.find("end").text),
                                  word_node.find("text").text, syllables))
            lines.append(Line(int(line_node.find("begin").text), int(line_node.find("end").text),
                              line_node.find("text").text, words))
        self.text = root.find("text").text
        self.lines = lines
        return self
