# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Считыватель файлов разных расширений.

from enum import Enum
from typing import Generator
import os
import xml.etree.ElementTree as etree
import json

from poetry.apps.corpus.scripts.main.markup import Markup
from poetry.apps.corpus.scripts.main.phonetics import Phonetics
from poetry.apps.corpus.scripts.accents.dict import AccentDict
from poetry.apps.corpus.scripts.accents.classifier import MLAccentClassifier
from poetry.apps.corpus.scripts.metre.metre_classifier import MetreClassifier


RAW_SEPARATOR = "\n\n\n"


class SourceTypeEnum(Enum):
    RAW = ".txt"
    XML = ".xml"
    JSON = ".json"


class SourceReader(object):
    @staticmethod
    def read_markups(source_type: SourceTypeEnum, is_folder: bool, is_processed: bool, path: str,
                     accents_dict: AccentDict=None,
                     accents_classifier: MLAccentClassifier=None) -> Generator[Markup, None, None]:
        if not is_processed:
            assert accents_dict is not None
            assert accents_classifier is not None
        paths = []
        if is_folder:
            paths = os.listdir(path)
        else:
            paths.append(path)
        paths = [p for p in paths if p.endswith(source_type.value)]

        for filename in paths:
            with open(filename, "r", encoding="utf-8") as file:
                if source_type == SourceTypeEnum.XML and not is_processed:
                    for elem in SourceReader.__xml_iter(file, 'item'):
                        text = elem.find(".//text").text
                        yield SourceReader.__process(text, accents_dict, accents_classifier)
                elif source_type == SourceTypeEnum.XML and is_processed:
                    for elem in SourceReader.__xml_iter(file, 'markup'):
                        markup = Markup()
                        markup.from_xml(etree.tostring(elem, encoding='utf-8', method='xml'))
                        yield markup
                elif source_type == SourceTypeEnum.JSON and not is_processed:
                    # TODO: ленивый парсинг
                    j = json.load(file)
                    for item in j['items']:
                        yield SourceReader.__process(item['text'], accents_dict, accents_classifier)
                elif source_type == SourceTypeEnum.JSON and is_processed:
                    j = json.load(file)
                    for item in j['items']:
                        markup = Markup()
                        markup.from_json(item)
                        yield markup
                elif source_type == SourceTypeEnum.RAW and not is_processed:
                    text = file.read()
                    for t in text.split(RAW_SEPARATOR):
                        yield SourceReader.__process(t, accents_dict, accents_classifier)
                elif source_type == SourceTypeEnum.RAW and is_processed:
                    raise NotImplementedError("Пока не реализовано.")

    @staticmethod
    def __process(text: str, accents_dict: AccentDict=None,
                  accents_classifier: MLAccentClassifier=None) -> Markup:
        markup = Phonetics.process_text(text, accents_dict)
        markup = MetreClassifier.improve_markup(markup, accents_classifier)[0]
        return markup

    @staticmethod
    def __xml_iter(file, tag):
        return (elem for event, elem in etree.iterparse(file, events=['end']) if event == 'end' and elem.tag == tag)



