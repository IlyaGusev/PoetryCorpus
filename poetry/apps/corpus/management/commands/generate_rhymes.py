# -*- coding: utf-8 -*-
import os

from django.core.management.base import BaseCommand
from poetry.apps.corpus.scripts.rhymes.rhymes import Rhymes


class Command(BaseCommand):
    help = 'Rhymes generation'

    def handle(self, *args, **options):
        Rhymes.get_all_rhymes()