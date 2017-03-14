# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты к классификатору метра.

import os
import unittest
import jsonpickle

from poetry.apps.corpus.scripts.accents.dict import AccentDict
from poetry.apps.corpus.scripts.main.phonetics import Phonetics
from poetry.apps.corpus.scripts.metre.metre_classifier import MetreClassifier, ClassificationResult, AccentCorrection
from poetry.settings import BASE_DIR


class TestMetreClassifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accent_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict"))

    def test_classification_result(self):
        result = ClassificationResult(5)
        result.additions["iambos"].append(AccentCorrection(0, 0, 0, "", 0))
        self.assertEqual(result, jsonpickle.decode(result.to_json()))

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

        text = "Вот уж вечер. Роса\n" \
               "Блестит на крапиве.\n"\
               "Я стою у дороги,\n"\
               "Прислонившись к иве.\n"\
               "От луны свет большой\n"\
               "Прямо на нашу крышу.\n"\
               "Где-то песнь соловья\n"\
               "Хорошо и тепло,\n"\
               "Как зимой у печки.\n"\
               "И березы стоят,\n"\
               "Как большие свечки.\n"\
               "И вдали за рекой,\n"\
               "Видно, за опушкой,\n"\
               "Сонный сторож стучит\n"\
               "Мертвой колотушкой."
        result_metre = MetreClassifier.classify_metre(Phonetics.process_text(text, self.accent_dict)).metre
        self.assertTrue(result_metre == "dolnik3" or result_metre == "dolnik2")

        text = "Глыбу кварца разбили молотом,\n" \
               "И, веселым огнем горя,\n" \
               "Заблестели крупинки золота\n" \
               "В свете тусклого фонаря.\n" \
               "И вокруг собрались откатчики:\n" \
               "Редкий случай, чтоб так, в руде!\n" \
               "И от ламп заплясали зайчики,\n" \
               "Отражаясь в черной воде...\n" \
               "Прислонившись к мокрой стене,\n" \
               "Мы стояли вокруг.\n" \
               "Курили,\n" \
               "Прислонившись к мокрой стене,\n" \
               "И мечтательно говорили\n" \
               "Не о золоте — о весне.\n" \
               "И о том, что скоро, наверно,\n" \
               "На заливе вспотеет лед\n" \
               "И, снега огласив сиреной,\n" \
               "Наконец придет пароход...\n" \
               "Покурили еще немного,\n" \
               "Золотинки в кисет смели\n" \
               "И опять — по своим дорогам,\n" \
               "К вагонеткам своим пошли.\n" \
               "Что нам золото? В дни тяжелые\n" \
               "Я от жадности злой не слеп.\n" \
               "Самородки большие, желтые\n" \
               "Отдавал за табак и хлеб.\n" \
               "Не о золоте были мысли...\n" \
               "В ночь таежную у костра\n" \
               "Есть над чем поразмыслить в жизни,\n" \
               "Кроме\n" \
               "Золота-серебра."
        result_metre = MetreClassifier.classify_metre(Phonetics.process_text(text, self.accent_dict)).metre
        self.assertTrue(result_metre == "dolnik3" or result_metre == "dolnik2")

        MetreClassifier.improve_markup(Phonetics.process_text(text, self.accent_dict))
