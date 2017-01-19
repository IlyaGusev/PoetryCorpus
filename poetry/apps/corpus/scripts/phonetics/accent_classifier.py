# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Расстановка ударений на основе машинного обучения

import gc
import os

import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.externals import joblib
from sklearn.model_selection import ShuffleSplit, cross_val_score

from poetry.apps.corpus.scripts.preprocess import CYRRILIC_LOWER_CONSONANTS, CYRRILIC_LOWER_VOWELS, VOWELS
from poetry.apps.corpus.scripts.phonetics.phonetics import Phonetics


class AccentClassifier:
    # TODO: Рефакторинг.
    def __init__(self, model_dir, accents_dict):
        if not os.path.isfile(os.path.join(model_dir, "clf_2.pickle")):
            self.build_accent_classifiers(model_dir, accents_dict)
        self.classifiers = {l: joblib.load(
            os.path.join(model_dir, "clf_" + str(l) + ".pickle")) for l in range(2, 13)}

    def generate_sample(self, syllables):
        l = len(syllables)
        features = []
        for i in range(0, l):
            text = syllables[i].text
            features.append(text[-1] in VOWELS)
            features.append(len(text))
            for ch1 in CYRRILIC_LOWER_CONSONANTS + CYRRILIC_LOWER_VOWELS:
                features.append(sum([ch1 == ch2 for ch2 in text]))
        return features

    def build_accent_classifiers(self, model_dir, accents_dict):
        if not os.path.exists(model_dir):
            os.mkdir(model_dir)
        train_syllables = {k: [] for k in range(2, 13)}
        answers = {k: [] for k in range(2, 13)}
        for key, accents in accents_dict.data.items():
            syllables = Phonetics.get_word_syllables(key)
            if len(syllables) >= 2:
                for syllable in syllables:
                    if "ё" not in key:
                        for accent in accents:
                            if syllable.begin <= accent < syllable.end:
                                syllable.accent = accent
                                answer = syllable.number
                                answers[len(syllables)].append(answer)
                                train_syllables[len(syllables)].append(syllables)

        for l in range(2, 13):
            train_data = []
            for syllables in train_syllables[l]:
                train_data.append(self.generate_sample(syllables))
            clf = DecisionTreeClassifier()
            clf.fit(train_data, answers[l])
            joblib.dump(clf, os.path.join(model_dir, "clf_" + str(l) + ".pickle"))
            cv = ShuffleSplit(2, test_size=0.2, random_state=10)
            cv_scores = cross_val_score(clf, train_data, answers[l], cv=cv, scoring='accuracy')
            print(str(l) + " syllables. Accuracy: %0.3f (+/- %0.3f)" % (cv_scores.mean(), cv_scores.std() * 2))
            del clf
            del train_syllables[l]
            del answers[l]
            del train_data
            gc.collect()

    def classify_accent(self, words):
        answers = []
        for word in words:
            syllables = Phonetics.get_word_syllables(word)
            answer = self.classifiers[len(syllables)].predict(np.array(self.generate_sample(syllables)).reshape(1, -1))
            answers.append(answer[0])
        return answers
