# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты к классификатору метра.

import unittest
import os

from poetry.settings import BASE_DIR
from poetry.apps.corpus.scripts.phonetics.accent_dict import AccentDict
from poetry.apps.corpus.scripts.phonetics.phonetics import Phonetics
from poetry.apps.corpus.scripts.metre.metre_classifier import MetreClassifier


class TestMetreClassifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accent_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict"))

    def test_metre_classifier(self):

        text = "Горит восток зарёю новой.\n" \
               "Уж на равнине, по холмам\n" \
               "Грохочут пушки. Дым багровый\n" \
               "Кругами всходит к небесам."
        result_metre = MetreClassifier.classify_metre(Phonetics.process_text(text, self.accent_dict)).metre
        self.assertEqual(result_metre, "iambos")

        text = "Буря мглою небо кроет,\n" \
               "Вихри снежные крутя;\n" \
               "То, как зверь, она завоет,\n" \
               "То заплачет, как дитя..."
        result_metre = MetreClassifier.classify_metre(Phonetics.process_text(text, self.accent_dict)).metre
        self.assertEqual(result_metre, "choreios")

        text = "На стеклах нарастает лед,\n"\
               "Часы твердят: «Не трусь!»\n"\
               "Услышать, что ко мне идет,\n"\
               "И мертвой я боюсь.\n"\
               "Как идола, молю я дверь;\n"\
               "«Не пропускай беду!»\n"\
               "Кто воет за стеной, как зверь,\n"\
               "Кто прячется в саду?"
        result_metre = MetreClassifier.classify_metre(Phonetics.process_text(text, self.accent_dict)).metre
        self.assertEqual(result_metre, "iambos")

        MetreClassifier.improve_markup(Phonetics.process_text(text, self.accent_dict))
