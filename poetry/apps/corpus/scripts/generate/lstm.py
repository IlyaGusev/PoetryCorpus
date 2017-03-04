import os
from collections import Counter
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.optimizers import RMSprop
import numpy as np
import random
import sys
import xml.etree.ElementTree as etree
from poetry.settings import BASE_DIR
from poetry.apps.corpus.scripts.preprocess import text_to_wordlist

UNKNOWN_WORD = "#########"


def get_batch(text, words, word_indices, pos, size, sentence_length, step):
    sentences = []
    next_words = []
    end = pos+size
    if end > len(text) - sentence_length:
        end = len(text) - sentence_length
    for i in range(pos, end, step):
        sentences.append(text[i: i + sentence_length])
        next_words.append(text[i + sentence_length])
    X = np.zeros((len(sentences), sentence_length, len(words)), dtype=np.bool)
    y = np.zeros((len(sentences), len(words)), dtype=np.bool)
    for i, sentence in enumerate(sentences):
        for t, word in enumerate(sentence):
            if word in words:
                X[i, t, word_indices[word]] = 1
            else:
                X[i, t, word_indices[UNKNOWN_WORD]] = 1
        if next_words[i] in words:
            y[i, word_indices[next_words[i]]] = 1
        else:
            y[i, word_indices[UNKNOWN_WORD]] = 1
    return X, y


def build_model(words, sentence_length):
    model = Sequential()
    model.add(LSTM(128, input_shape=(sentence_length, len(words)), stateful=False))
    model.add(Dense(len(words)))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy', optimizer=RMSprop(lr=0.005))
    return model


def sample(preds, temperature=1.0):
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


def train():
    root = etree.parse(os.path.join(BASE_DIR, "datasets", "corpus", "all.xml")).getroot()
    words_counter = Counter()
    for item in root.iterfind("./item"):
        for line in item.find("./text").text.split("\n"):
            for word in text_to_wordlist(line):
                words_counter[word] += 1
            words_counter["\n"] += 1
    words = [i[0] for i in words_counter.most_common(60000)] + [UNKNOWN_WORD]
    word_indices = dict((c, i) for i, c in enumerate(words))
    sentence_length = 10

    model = build_model(words, sentence_length)
    for iteration in range(1, 60):
        print()
        print('-' * 50)
        print('Iteration', iteration)
        size = 8192
        text = []
        text_index = 0
        for item in root.iterfind("./item"):
            for line in item.find("./text").text.split("\n"):
                text += text_to_wordlist(line)
                text.append("\n")
            if len(text) >= size:
                x, y = get_batch(text, words, word_indices, 0, size, sentence_length, 3)
                model.fit(x, y, batch_size=128, nb_epoch=1)
                text[:] = []
            text_index += 1
            if text_index % 1000 == 0:
                print(text_index)

        start_index = random.randint(0, len(text) - 1 - 1)

        generated = ''
        sentence = text[start_index: start_index + sentence_length]
        generated += " ".join(sentence)
        print('----- Generating with seed: "' + str(sentence) + '"')
        sys.stdout.write(generated)

        for i in range(50):
            x = np.zeros((1, sentence_length, len(words)))
            for t, word in enumerate(sentence):
                if word in words:
                    x[0, t, word_indices[word]] = 1.

            preds = model.predict(x, verbose=0)[0]
            next_word = UNKNOWN_WORD
            while next_word == UNKNOWN_WORD:
                next_word = np.random.choice(words, 1, p=preds)[0]

            generated += next_word
            sentence = sentence[1:] + [next_word]

            sys.stdout.write(" " + next_word)
            sys.stdout.flush()
train()