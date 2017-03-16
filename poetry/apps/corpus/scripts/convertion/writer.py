# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Запись в файлы разных расширений.

from enum import Enum
from typing import List

from poetry.apps.corpus.scripts.convertion.reader import RAW_SEPARATOR
from poetry.apps.corpus.scripts.main.markup import Markup


class DestinationTypeEnum(Enum):
    RAW = ".txt"
    XML = ".xml"
    JSON = ".json"


class DestinationWriter(object):
    @staticmethod
    def write_markups(destination_type: DestinationTypeEnum, markups: List[Markup], path: str) -> None:
        with open(path, "w", encoding="utf-8") as file:
            if destination_type == DestinationTypeEnum.XML:
                file.write('<?xml version="1.0" encoding="UTF-8"?><items>')
                for markup in markups:
                    xml = markup.to_xml().encode('utf-8')\
                        .replace(b'<?xml version="1.0" encoding="UTF-8" ?>', b'').decode('utf-8')
                    file.write(xml)
                file.write('</items>')
            elif destination_type == DestinationTypeEnum.JSON:
                file.write("[")
                for markup in markups:
                    file.write(markup.to_json())
                    file.write(",")
                file.seek(0, 2)
                size = file.tell()
                file.truncate(size - 1)
                file.write(']')
            elif destination_type == DestinationTypeEnum.RAW:
                for markup in markups:
                    for line in markup.lines:
                        for word in line.words:
                            file.write(word.get_short())
                        file.write("\n")
                    file.write(RAW_SEPARATOR)

