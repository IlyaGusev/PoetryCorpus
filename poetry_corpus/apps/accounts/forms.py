# -*- coding: utf-8 -*-

import re

from django.forms import ValidationError, ModelForm, Form, CharField, PasswordInput, TextInput
from django.utils.translation import ugettext_lazy as _
from accounts.models import MyUser


class SignUpForm(ModelForm):
    """
    Регистрационная форма.
    """
    password = CharField(label=_('Пароль'), widget=PasswordInput(attrs={'placeholder': _('Пароль')}))
    password_repeat = CharField(label=_('Пароль ещё раз'), widget=PasswordInput(attrs={'placeholder': _('Пароль ещё раз')}))

    class Meta:
        model = MyUser
        fields = ('email', 'organisation', 'last_name', 'first_name')
        labels = {
            'email': _('E-mail'),
            'first_name': _('Имя'),
            'last_name': _('Фамилия'),
            'organisation': _('Организация')
        }
        widgets = {
            'email': TextInput(attrs={'placeholder': _('E-mail')}),
            'first_name': TextInput(attrs={'placeholder': _('Имя')}),
            'last_name': TextInput(attrs={'placeholder': _('Фамилия')}),
            'organisation': TextInput(attrs={'placeholder': _('Организация')}),
        }

    def clean_first_name(self):
        r = re.compile(u'^[А-ЯЁ][а-яё]*$', re.UNICODE)
        res = r.match(self.cleaned_data['first_name'])
        if res is None:
            raise ValidationError(
                _('Неверный формат имени: первыя буква должна быть заглавной, допустимы только русские символы.'))
        return self.cleaned_data['first_name']

    def clean_last_name(self):
        r = re.compile(u'^[А-ЯЁ][а-яё]+$', re.UNICODE)
        res = r.match(self.cleaned_data['last_name'])
        if res is None:
            raise ValidationError(
                _('Неверный формат фамилии: первыя буква должна быть заглавной, допустимы только русские символы.'))
        return self.cleaned_data['last_name']

    def clean_password(self):
        l = len(self.cleaned_data['password'])
        if l <= 5 or l >= 30:
            raise ValidationError(
                _('Неверная длина пароля.'))
        return self.cleaned_data['password']

    def clean_password_repeat(self):
        pass1 = self.data['password']
        pass2 = self.data['password_repeat']
        if pass1 != pass2:
            raise ValidationError(
                _("Пароли не совпадают."))
        return pass2

    def clean_email(self):
        if MyUser.objects.filter(email=self.cleaned_data['email']).exists():
            raise ValidationError(_('Этот e-mail уже используется.'))
        return self.cleaned_data['email']
