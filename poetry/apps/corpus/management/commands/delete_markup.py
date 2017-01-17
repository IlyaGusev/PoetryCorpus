# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from poetry.apps.corpus.models import Poem, Markup


class Command(BaseCommand):
    help = 'Automatic markup update'

    def handle(self, *args, **options):
        for poem in Poem.objects.all():
            Markup.objects.filter(poem=poem, author="Automatic").delete()

