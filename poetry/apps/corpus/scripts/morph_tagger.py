import xml.etree.ElementTree as etree

import pymorphy2

from poetry.apps.corpus.scripts.util.preprocess import text_to_sentences
from poetry.apps.corpus.scripts.util.preprocess import text_to_wordlist


def main():
    morph_ru = pymorphy2.MorphAnalyzer() #pymorphy2 
    tree = etree.parse("../datasets/all.xml")
    root = tree.getroot()

    root_to_write = etree.Element("root")
    doc = etree.SubElement(root_to_write, "doc")
    for item in root.findall(".//item"):
        names = item.findall(".//name")
        if len(names) == 0:
            continue
        item_to_write = etree.SubElement(doc, "item")
        name_to_write = etree.SubElement(item_to_write, "name")
        name_to_write.text = names[0].text
        print(name_to_write.text)
        content = item.findall(".//text")[0].text
        for sentence in text_to_sentences(content):
            for word in text_to_wordlist(sentence):  
                word_to_write = etree.SubElement(item_to_write, "word")
                word_to_write.text = word

                result = morph_ru.parse(word)  # Return several alternatives           
                for alter in result:
                    etree.SubElement(word_to_write, "morphotag").text = str(alter.tag)
    print('Printing results')
    tree_to_write = etree.ElementTree(root_to_write)
    tree_to_write.write("morpho_result.xml",encoding="UTF-8",xml_declaration=True)
    print('End.')

main()
