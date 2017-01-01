import random
from poetry_corpus.scripts.preprocess import text_to_wordlist
from poetry_corpus.scripts.phonetics.phonetics import Phonetics
from numpy.random import choice


class Markov(object):
    def __init__(self, n_prev=1):
        self.transitions = {}
        self.transitions_inverse = {}
        self.n_prev = n_prev
        self.rhymes = {}

    def generate_chain(self, words, transitions):
        for i in range(len(words) - self.n_prev):
            current_words = " ".join([words[j] for j in range(i, i + self.n_prev)])
            next_word = words[i + self.n_prev]

            if transitions.get(current_words) is None:
                transitions[current_words] = {}
            transition = transitions[current_words]

            if transition.get(next_word) is None:
                transition[next_word] = 0
            transition[next_word] += 1
        return transitions

    def add_text(self, markup):
        words = []
        for line in markup.lines:
            for word in line.words:
                words.append(word.text.lower())

        self.generate_chain(words, self.transitions)
        self.generate_chain(list(reversed(words)), self.transitions_inverse)
        rhymes = Phonetics.get_all_rhymes(markup)
        for first_word, mapping in rhymes.items():
            for second_word, freq in mapping.items():
                if self.rhymes.get(first_word) is None:
                    self.rhymes[first_word] = {}
                if self.rhymes[first_word].get(second_word) is None:
                    self.rhymes[first_word][second_word] = 0
                self.rhymes[first_word][second_word] += freq

    def generate_markov_text(self, transitions, size=25, seed_words=None):
        if seed_words is None:
            seed_words = choice(list(transitions.keys()), 1)[0]
        gen_words = [seed_words]
        text = seed_words[:]
        for i in range(size-self.n_prev):
            if transitions.get(gen_words[i]) is not None:
                transition = transitions[gen_words[i]]
                candidates = list(transition.keys())
                weights = list(transition.values())
                weights = [w / sum(weights) for w in weights]
                next_words = choice(candidates, 1, p=weights)[0]
            else:
                next_words = gen_words[i]
            gen_words.append(" ".join(gen_words[i].split(" ")[1:] + [next_words]))
            text += " " + next_words
        return text

    def generate_poem(self, n_lines=4, n_words=4):
        candidates = list(self.rhymes.keys())

        last_word1 = choice(candidates, 1)[0]
        last_word2 = choice(candidates, 1)[0]
        first_line = " ".join(reversed(self.generate_markov_text(self.transitions_inverse, n_words, last_word1).split(" ")))
        second_line = " ".join(reversed(self.generate_markov_text(self.transitions_inverse, n_words, last_word2).split(" ")))

        candidates = list(self.rhymes[last_word1].keys())
        weights = list(self.rhymes[last_word1].values())
        weights = [w / sum(weights) for w in weights]
        last_word3 = choice(candidates, 1, p=weights)[0]
        candidates = list(self.rhymes[last_word2].keys())
        weights = list(self.rhymes[last_word2].values())
        weights = [w / sum(weights) for w in weights]
        last_word4 = choice(candidates, 1, p=weights)[0]

        third_line = " ".join(reversed(self.generate_markov_text(self.transitions_inverse, n_words, last_word3).split(" ")))
        forth_line = " ".join(reversed(self.generate_markov_text(self.transitions_inverse, n_words, last_word4).split(" ")))
        return first_line + "\n" + second_line + "\n" + third_line + "\n" + forth_line + "\n"
