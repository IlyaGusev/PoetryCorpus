# -*- coding: utf-8 -*-

from urllib import parse

from django.forms import Form, CharField, IntegerField, Textarea


class GeneratorForm(Form):
    """
    Форма генератора стихов.
    """
    metre_schema = CharField(label="Схема метра (+/-)", initial="+-")
    rhyme_schema = CharField(label="Схема рифмовки (a/b/c)", max_length=30, initial="aabb")
    syllables_count = IntegerField(label="Количество слогов в строке", min_value=2, max_value=20, initial=8)

    def as_url_args(self):
        if self.is_valid():
            return parse.urlencode(self.cleaned_data)
        return ""


class AccentsForm(Form):
    """
    Форма определения ударения слова.
    """
    word = CharField(label="Слово", max_length=30)


class RhymesForm(Form):
    """
    Форма подбора рифм
    """
    word = CharField(label="Слово", max_length=30)


class AnalysisForm(Form):
    """
    Форма анализа стиховторения
    """
    text = CharField(label="Стихотворение для анализа", max_length=25000, widget=Textarea)