import xml.etree.ElementTree as etree
import codecs
from math import log, sqrt

from poetry_corpus.scripts.preprocess import text_to_wordlist


def collectNgrams():
    bigrams = {}
    unigrams = {}
    tree = etree.parse("./../../datasets/all.xml")

    root = tree.getroot()
    for text in root.findall(".//text"):
        content = text.text
        wordList = text_to_wordlist(content)
        for i in range(len(wordList) - 1):
            bigram = wordList[i] + "$" + wordList[i + 1]
            bigrams.setdefault(bigram, 0)
            bigrams[bigram] += 1
            unigrams.setdefault(wordList[i], 0)
            unigrams[wordList[i]] += 1
        unigrams.setdefault(wordList[-1], 0)
        unigrams[wordList[-1]] += 1
    return bigrams, unigrams


def sortAndWrite(dic, path):
    frecToKey = [ [value,key] for key, value in dic.items()]
    sortedByFreq = [value + "\t" + str(key) for key, value in sorted(frecToKey, key = lambda x: x[0], reverse=True)]
    with codecs.open(path, "w", "utf-8") as f:
        f.write("\n".join(sortedByFreq))


def calcMeasures(bigrams, unigrams):
    MImeasure = {}
    Tmeasure = {}
    MIAmeasure = {}
    HImeasure = {}
    ORmeasure = {}
    DICEmeasure = {}

    nBigrams = len(bigrams.keys())
    nUnigrams = len(unigrams.keys())
    for key, value in bigrams.items():
        word1, word2 = key.split("$")
        value = float(value)
        p0 = unigrams[word1] * unigrams[word2]
        e11 = p0
        e12 = unigrams[word1] * (nUnigrams - unigrams[word2])
        e21 = (nUnigrams - unigrams[word1]) * unigrams[word2]
        e22 = (nUnigrams - unigrams[word1]) * (nUnigrams - unigrams[word2])
        e = [ p0, unigrams[word1] * (nUnigrams - unigrams[word2]),
        (nUnigrams - unigrams[word1]) * unigrams[word2], (nUnigrams - unigrams[word1]) * (nUnigrams - unigrams[word2])]

        c = [value, unigrams[word2]-value,
        unigrams[word1] - value, nBigrams - value
        ]
        #print(e, c)

        MImeasure[key] =log(float(value) * nUnigrams * nUnigrams/(nBigrams * unigrams[word1]*unigrams[word2]))
        Tmeasure[key] =  (float(value) - p0*nBigrams)/sqrt(float(value))

        #mia = sum([c[i] * log(float(c[i])/e[i], 2) for i in range(4)])
        #MIAmeasure[key] = mia

        hi = sum([(c[i]-e[i]) * (c[i]-e[i]) / float(e[i]) for i in range(4)])
        HImeasure[key] = hi

        OR = (float(c[0]) + 0.5)/(c[2] + 0.5) * (c[1] + 0.5)/(c[3] + 0.5)
        ORmeasure[key] = OR

        DICE = 2 * value/(unigrams[word2] + unigrams[word1])
        DICEmeasure[key] = DICE
    sortAndWrite(MImeasure, "./../../bigrams/bigramsMIScore.txt")
    sortAndWrite(Tmeasure, "./../../bigrams/bigramsTScore.txt")
    sortAndWrite(HImeasure, "./../../bigrams/bigramsHIScore.txt")
    sortAndWrite(ORmeasure, "./../../bigrams/bigramsORScore.txt")
    sortAndWrite(DICEmeasure, "./../../bigrams/bigramsDICEScore.txt")

    #with codecs.open("./../../datasets/bigramsMIA.txt", "w", "utf-8") as f:
    #	f.write("\n".join(["\t".join(map(str, pair)) for pair in MIAmeasure]))



def main():
    bigrams, unigrams = collectNgrams()
    sortAndWrite(bigrams, "./../../bigramsSorted.txt")
    calcMeasures(bigrams, unigrams)

main()