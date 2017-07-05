from django.core.management.base import BaseCommand
from poetry.apps.corpus.models import Poem, MarkupInstance, Markup


class Command(BaseCommand):
    def handle(self, *args, **options):
        auto = Markup.objects.create(name="Automatic")
        manual = Markup.objects.create(name="Manual")
        instances = MarkupInstance.objects.all()
        for instance in instances:
            if instance.author == "Automatic":
                instance.markup = auto
            else:
                instance.markup = manual
            instance.save()
