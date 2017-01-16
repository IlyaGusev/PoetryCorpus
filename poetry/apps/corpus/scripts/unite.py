import itertools
import re
import xml.etree.ElementTree as etree
import os

from dicttoxml import dicttoxml

from poetry.settings import BASE_DIR
from poetry.apps.corpus.scripts.preprocess import to_cyrrilic, normilize_line


def clean_text(text):
    if text is None:
        return None
    new_text = []
    regexp = "[^а-яА-Яёa-zA-Z,.;-?!]"
    for line in text.split("\n"):
        if len(re.sub(regexp, "", line)) != 0:
            new_text.append(line.strip())
    return "\n".join(new_text)


def get_actual_line(text, index):
    regexp = "[^а-яА-Яёa-zA-Z\n]"
    text = to_cyrrilic(re.sub(regexp, "", text).strip().lower())
    lines = text.split("\n")
    if index > len(lines) - 1:
        return lines[len(lines)-1]
    return lines[index]


class Corpus:
    def __init__(self):
        self.data = []
        self.invalid_count = 0
        self.duplicates_count = 0
        self.concatenated_count = 0
        self.themes_not_assigned_count = 0

    def process_file(self, file_name, item_node_name, fields):
        tree = etree.parse(file_name)
        root = tree.getroot()
        for item in root.findall(item_node_name):
            element = dict()
            valid = True
            for name, properties in fields.items():
                element[name] = properties['handler'](item.find(properties['path']))
                if element[name] == "":
                    element[name] = None
                if properties['required'] and element[name] is None:
                    valid = False
                    self.invalid_count += 1
            if valid:
                self.data.append(element)

    def generate_id(self, element):
        if element['name'] is not None:
            name = normilize_line(element['name'])
        else:
            name = get_actual_line(element['text'], 0)
        return normilize_line(element['author']) + " " + name

    def clean_duplicates(self):
        data = dict()
        for element in self.data:
            id = self.generate_id(element)
            if data.get(id) is None:
                if element['text'] is None:
                    self.themes_not_assigned_count += 1
                    continue
                data[id] = element
                themes = element['themes']
                data[id]['themes'] = set()
                if themes is not None:
                    for theme in themes:
                        data[id]['themes'].add(theme)
            else:
                if element['text'] is None:
                    if element['themes'] is not None:
                        for theme in element['themes']:
                            data[id]['themes'].add(theme)
                elif data[id]['text'] is None:
                    element['themes'] = data[id]['themes']
                    data[id] = element
                else:
                    is_duplicate = False
                    for i in range(3):
                        for j in range(3):
                            flag1 = get_actual_line(element['text'], i) in get_actual_line(data[id]['text'], j)
                            flag2 = get_actual_line(data[id]['text'], i) in get_actual_line(element['text'], j)
                            is_duplicate = is_duplicate or flag1 or flag2
                    if not is_duplicate:
                        # TODO: handle this case
                        self.concatenated_count += 1
                    else:
                        for field, value in data[id].items():
                            if value is None:
                                data[id][field] = element[field]
                        if len(element['text']) > len(data[id]['text']):
                            data[id]['text'] = element['text']
                        self.duplicates_count += 1
        self.data = list(data.values())
        for i in range(len(self.data)):
            self.data[i]['themes'] = list(self.data[i]['themes'])

    def to_xml(self, filename):
        with open(filename, 'wb') as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?><items>')
            for element in self.data:
                xml = dicttoxml(element, custom_root='item', attr_type=False)\
                    .replace(b'<?xml version="1.0" encoding="UTF-8" ?>', b'')
                f.write(xml)
            f.write(b'</items>')

    def to_sketch(self, filename, fields):
        with open(filename, 'w', encoding='utf-8') as f:
            content = '<?xml version="1.0" encoding="UTF-8"?><items>'
            for element in self.data:
                xml = '<doc '
                for field in fields.keys():
                    if element[field] is not None and field not in ['themes', 'text']:
                        xml += ' ' + field + '="{0}"'.format(element[field])
                xml += '>' + element['text'] + '</doc>'
                content += xml
            content += '</items>'
            f.write(content)

    def to_django(self, filename, themes_filename, fields):
        themes_to_pk = dict()
        with open(themes_filename, 'w', encoding='utf-8') as f:
            themes = list(set(list(itertools.chain.from_iterable([element['themes'] for element in self.data]))))
            pk = 1
            content = '['
            for theme in themes:
                themes_to_pk[theme] = pk
                content += '{"model": "corpus.Theme", "pk": ' + str(pk) + \
                           ', "fields": {"theme": ' + '"' + theme + '"}},'
                pk += 1
            content = content[:-1] + ']'
            f.write(content)

        with open(filename, 'w', encoding='utf-8') as f:
            pk = 1
            content = '['
            for element in self.data:
                content += '{"model": "corpus.Poem", "pk": ' + str(pk) + ', "fields": {'
                for field in fields.keys():
                    if element[field] is not None and field not in ['themes']:
                        escaped_element = str(element[field]).replace("\n", "\\n")\
                            .replace('"', '\\"')\
                            .replace("\t", "\\t")
                        content += '"' + str(field) + '": "' + escaped_element + '",'
                    elif field == 'themes':
                        if len(element['themes']) == 0:
                            theme_list = "[]"
                        else:
                            theme_list = "["
                            for theme in element['themes']:
                                theme_list += str(themes_to_pk[theme]) + ","
                            theme_list = theme_list[:-1] + "]"
                        content += '"' + str(field) + '": ' + theme_list + ','
                content = content[:-1] + '}},'
                pk += 1
            content = content[:-1] + ']'
            f.write(content)


def main():
    corpus = Corpus()
    text_files = [os.path.join(BASE_DIR, "datasets", "strofa.xml"), os.path.join(BASE_DIR, "datasets", "klassika.xml"),
                  os.path.join(BASE_DIR, "datasets", "rupoem.xml")]
    themes_files = [os.path.join(BASE_DIR, "datasets", "themes.xml")]
    fields = {
        'name': {
            'path': './/name',
            'handler': lambda x: x if x is None else x.text,
            'required': False
        },
        'author': {
            'path': './/author',
            'handler': lambda x: x if x is None else x.text,
            'required': True
        },
        'text': {
            'path': './/text',
            'handler': lambda x: x if x is None else clean_text(x.text),
            'required': True
        },
        'date_from': {
            'path': './/date_from',
            'handler': lambda x: x if x is None else int(x.text),
            'required': False
        },
        'date_to': {
            'path': './/date_to',
            'handler': lambda x: x if x is None else int(x.text),
            'required': False
        },
        'themes': {
            'path': './/themes',
            'handler': lambda x: [] if x is None else [value.text for value in x.findall(".//value")],
            'required': False
        },
    }
    for filename in text_files:
        corpus.process_file(filename, './/item', fields)

    fields['text']['required'] = False
    fields['themes']['required'] = True
    for filename in themes_files:
        corpus.process_file(filename, './/item', fields)

    corpus.clean_duplicates()

    # Statistics
    print("Example:", corpus.data[0])
    print("Invalid: ", corpus.invalid_count)
    print("Duplicates: ", corpus.duplicates_count)
    print("Concatenated: ", corpus.concatenated_count)
    print("Total chars: ", sum([len(elem['text']) for elem in corpus.data]))
    print("Total words: ", sum([len(elem['text'].split()) for elem in corpus.data]))
    print("Total poems after deduplication: ", len(corpus.data))
    print("Total poems with themes: ", len([elem for elem in corpus.data if len(elem['themes']) != 0]))
    authors = set()
    for elem in corpus.data:
        authors.add(normilize_line(elem['author']))
    print("Total authors: ", len(authors))

    # corpus.to_sketch("../datasets/all_sketch.xml", fields)
    corpus.to_django(os.path.join(BASE_DIR, "datasets", "all_django.json"),
                     os.path.join(BASE_DIR, "datasets", "themes_django.json"), fields)
main()