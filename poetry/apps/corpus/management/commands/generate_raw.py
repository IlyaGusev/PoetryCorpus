import os

from django.core.management.base import BaseCommand
from poetry.apps.corpus.models import Poem
from poetry.settings import BASE_DIR


class Command(BaseCommand):
    def handle(self, *args, **options):
        poems = Poem.objects.all()
        directory = os.path.join(BASE_DIR, "datasets", "corpus", "all_raw")
        if os.path.exists(directory):
            for path in os.listdir(directory):
                os.remove(os.path.join(directory, path))
        else:
            os.mkdir(directory)
        for i, poem in enumerate(poems):
            print(i, poem.name)
            try:
                filename = poem.author.replace(" ","")+poem.get_name_short()+".txt"
                with open(os.path.join(directory, filename), 'w', encoding="utf-8") as f:
                    f.write(poem.text)
            except Exception:
                pass