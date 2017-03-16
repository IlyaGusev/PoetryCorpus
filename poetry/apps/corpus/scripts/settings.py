import os
from poetry.settings import BASE_DIR

DICT_PATH = os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict")
CLASSIFIER_PATH = os.path.join(BASE_DIR, "datasets", "models")
MARKUPS_DUMP_XML_PATH = os.path.join(BASE_DIR, "datasets", "corpus", "markup_dump.xml")
MARKUPS_DUMP_RAW_PATH = os.path.join(BASE_DIR, "datasets", "corpus", "markup_dump.txt")
POEMS_DUMP_PATH = os.path.join(BASE_DIR, "datasets", "corpus", "all.xml")
MARKOV_PICKLE = os.path.join(BASE_DIR, "datasets", "markov.pickle")