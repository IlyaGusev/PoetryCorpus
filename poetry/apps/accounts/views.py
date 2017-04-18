# -*- coding: utf-8 -*-

from django.views.generic.edit import FormView, View
from django.core.urlresolvers import reverse_lazy
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth import authenticate, login

from accounts.models import MyUser
from accounts.forms import SignUpForm


class SignUpView(FormView):
    """
    Страница регистрации пользователя. Пользователь создаётся НЕ активным, нужно подтверждение.
    Дополнительные действия - установка стандартной аватарки.
    """
    template_name = 'accounts/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('about')

    def form_valid(self, form):
        form = form.cleaned_data
        user = MyUser.objects.create_user(email=form['email'], password=form['password'],
                                          first_name=form['first_name'], last_name=form['last_name'],
                                          organisation=form['organisation'])
        user.save()
        user = authenticate(email=form['email'], password=form['password'])
        login(self.request, user)
        return super(SignUpView, self).form_valid(form)


class CheckUniqueView(View):
    """
    Действие для проверки уникальности логина и почты.
    Клиентская часть в signup.js, функции check_username и check_email.
    """
    def get(self, request, *args, **kwargs):
        email = request.GET['email']
        result = {'email': '0'}
        if email != '':
            if MyUser.objects.all().filter(email=email).exists():
                result['email'] = '1'
        return JsonResponse(result, status=200)