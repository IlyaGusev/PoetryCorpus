# -*- coding: utf-8 -*-
import os

from django.core.management.base import BaseCommand
from poetry.apps.corpus.scripts.generate.markov import MarkovModelContainer


class Command(BaseCommand):
    help = 'Markov chains generation'

    def handle(self, *args, **options):
        MarkovModelContainer()