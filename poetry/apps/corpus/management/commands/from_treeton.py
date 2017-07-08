import os
import re

from django.core.management.base import BaseCommand
from poetry.apps.corpus.models import Poem, MarkupInstance, Markup
from poetry.settings import BASE_DIR


class Command(BaseCommand):
    def handle(self, *args, **options):
        poems = Poem.objects.all()
        directory = os.path.join(BASE_DIR, "datasets", "corpus", "all_raw")
        MarkupInstance.objects.filter(markup=Markup.objects.get(pk=3)).delete()
        for i, poem in enumerate(poems):
            filename = os.path.join(directory, poem.author.replace(" ", "") + poem.get_name_short() + ".txt.meta")
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()[1:]
                stress_lines = [re.sub(r"[^SUsu]+", "", line) for line in lines]
                markup_instances = poem.markup_instances.all()
                if len(markup_instances) != 0:
                    markup = poem.markup_instances.all()[0].get_markup()
                    assert len(markup.lines) == len(stress_lines)
                    for line_number, line in enumerate(markup.lines):
                        syllable_count = 0
                        for word in line.words:
                            syllable_count += len(word.syllables)
                        if len(stress_lines[line_number]) != syllable_count:
                            stress_lines[line_number] += "".join(["U" for _ in range(syllable_count-len(stress_lines[line_number]))])
                    for line_number, line in enumerate(markup.lines):
                        current_pos = 0
                        for word in line.words:
                            for k in range(len(word.syllables)):
                                letter = stress_lines[line_number][current_pos]
                                word.syllables[k].accent = word.syllables[k].vowel() if letter.lower() == "s" else -1
                                current_pos += 1
                    MarkupInstance.objects.create(poem=poem, text=markup.to_json(), author="Treeton", markup=Markup.objects.get(pk=3))
            i += 1
            print(i)
