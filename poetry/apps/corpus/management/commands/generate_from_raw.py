
# -*- coding: utf-8 -*-
import os

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Automatic markup dump for Django'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('--dir',
                            action='store',
                            dest='dir',
                            default="",
                            help='Dir')
        parser.add_argument('--out',
                            action='store',
                            dest='out',
                            default="",
                            help='Output')

    def handle(self, *args, **options):
        dir = options.get('dir')
        output = options.get('out')
        print(dir, output)
        with open(output, "w", encoding='utf-8') as f:
            content = '['
            for root, folders, files in os.walk(dir):
                for filename in files:
                    author = os.path.basename(filename).split(".")[0]
                    with open(os.path.join(dir, filename), "r", encoding="utf-8") as r:
                        text = r.read().replace("\\", "").replace("\n", "\\n").replace('"', '').replace("\t", "\\t")
                    for t in text.split("\\n\\n\\n"):
                        name = ""
                        for l in t.split("\\n"):
                            if l != '':
                                name = l
                                break
                        if name == "":
                            continue
                        print(name, author)
                        content += '{"model": "corpus.Poem", "fields": {"author": "' + author + \
                                   '", "name": "' + name + '", "text": "' + t + '"}},'
            content = content[:-1] + ']'
            f.write(content)