# -*- coding: utf-8 -*-
"""
    Авторы: Гусев Илья
    Дата создания: 22/07/2015
    Версия Python: 3.4
    Версия Django: 1.8.5
    Описание:
        Команда для создания суперпользователя со всеми правами при первом запуске.
        Использование: python3 manage.py create_superuser --username <username> --password <password>
"""
from django.core.management.base import BaseCommand, CommandError
from accounts.models import MyUser


class Command(BaseCommand):
    help = 'Creates/Updates an Admin user'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('--email',
                     action='store',
                     dest='email',
                     default=None,
                     help='Admin email')
        parser.add_argument('--password',
                     action='store',
                     dest='password',
                     default=None,
                     help='Admin password')

    def handle(self, *args, **options):
        email = options.get('email')
        password = options.get('password')
        if not email or not password:
            raise CommandError('You must specify email and password')
        MyUser.objects.create_superuser(email, "MIPT", password)
