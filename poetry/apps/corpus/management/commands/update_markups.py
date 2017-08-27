from django.core.management.base import BaseCommand
from poetry.apps.corpus.models import Poem, Markup, MarkupVersion


class Command(BaseCommand):
    def handle(self, *args, **options):
        manual = MarkupVersion.objects.get(name="Manual")
        markups = Markup.objects.all().exclude(author="Automatic")
        for markup in markups.iterator():
            markup.markup_version = manual
            markup.save()
