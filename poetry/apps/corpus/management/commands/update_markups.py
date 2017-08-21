from django.core.management.base import BaseCommand
from poetry.apps.corpus.models import Poem, Markup, MarkupVersion


class Command(BaseCommand):
    def handle(self, *args, **options):
        manual = MarkupVersion.objects.get(name="Manual")
        instances = Markup.objects.all().exclude(author="Automatic")
        for instance in instances.iterator():
            instance.markup = manual
            instance.save()
