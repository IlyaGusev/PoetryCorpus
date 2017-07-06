from django.core.management.base import BaseCommand
from poetry.apps.corpus.models import Poem, MarkupInstance, Markup


class Command(BaseCommand):
    def handle(self, *args, **options):
        manual = Markup.objects.get(name="Manual")
        instances = MarkupInstance.objects.all().exclude(author="Automatic")
        for instance in instances.iterator():
            instance.markup = manual
            instance.save()
