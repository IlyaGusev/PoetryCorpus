import random
from poetry_corpus.scripts.preprocess import text_to_wordlist
from numpy.random import choice


class Markov(object):
    def __init__(self, n_prev=1):
        self.transitions = {}
        self.n_prev = 1

    def add_text(self, text):
        words = text_to_wordlist(text)
        for i in range(len(words)-self.n_prev):
            current = " ".join([words[j] for j in range(i, i + self.n_prev)])
            next_word = words[i+self.n_prev]
            transition = self.transitions.get(current, {})
            if transition.get(next_word) is None:
                transition[next_word] = 1
            else:
                transition[next_word] += 1
            self.transitions[current] = transition

    def generate_markov_text(self, size=25):
        seed = random.randint(0, len(list(self.transitions.keys())))
        seed_words = list(self.transitions.keys())[seed]
        gen_words = [seed_words]
        text = seed_words
        for i in range(size):
            transition = self.transitions[gen_words[i]]
            candidates = []
            weights = []
            for word, weight in transition.items():
                candidates.append(word)
                weights.append(weight)
            weights = [w/sum(weights) for w in weights]
            next_word = choice(candidates, 1, p=weights)[0]
            gen_words.append(gen_words[i].split(" ")[1:] + next_word)
            text += " " + next_word
        return text
