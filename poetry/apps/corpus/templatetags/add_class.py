# -*- coding: utf-8 -*-
from django import template
register = template.Library()


# Добавление классов к элементам формы при её автоматической генерации
@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})