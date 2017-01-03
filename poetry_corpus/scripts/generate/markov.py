import random
from poetry_corpus.scripts.preprocess import text_to_wordlist
from poetry_corpus.scripts.phonetics.phonetics import Phonetics
from poetry_corpus.scripts.phonetics.phonetics_markup import CommonMixin
from numpy.random import choice


class Markov(CommonMixin):
    def __init__(self):
        self.transitions = {}
        self.transitions_inverse = {}
        self.rhymes = {}
        self.words_short = {}

    def generate_chain(self, words, transitions):
        for i in range(len(words) - 1):
            current_word = words[i].text.lower()
            next_word = words[i+1].get_short()
            self.words_short[next_word] = words[i+1]

            if transitions.get(current_word) is None:
                transitions[current_word] = {}
            transition = transitions[current_word]

            if transition.get(next_word) is None:
                transition[next_word] = 0
            transition[next_word] += 1
        return transitions

    def add_text(self, markup):
        words = []
        for line in markup.lines:
            for word in line.words:
                words.append(word)

        self.generate_chain(words, self.transitions)
        self.generate_chain(list(reversed(words)), self.transitions_inverse)
        rhymes = Phonetics.get_all_rhymes(markup)
        for first_word, mapping in rhymes.items():
            for second_word, freq in mapping.items():
                short1 = first_word.get_short()
                short2 = second_word.get_short()
                self.words_short[short1] = first_word
                self.words_short[short2] = second_word
                if self.rhymes.get(short1) is None:
                    self.rhymes[short1] = {}
                if self.rhymes[short1].get(short2) is None:
                    self.rhymes[short1][short2] = 0
                self.rhymes[short1][short2] += freq

    def filter_transition(self, transition, metre_pattern, n_syllables_max, position_in_pattern):
        filtered_transition = dict()
        for short, freq in transition.items():
            word = self.words_short[short]
            if len(word.syllables) > n_syllables_max:
                continue
            bad_word = False
            for i in range(len(word.syllables)):
                syllable = word.syllables[i]
                syllable_number = position_in_pattern + i
                if len(word.syllables) >= 2 and syllable.accent != -1 and metre_pattern[syllable_number] == "-":
                    bad_word = True
                    break
            if not bad_word:
                filtered_transition[short] = freq
        return filtered_transition

    def generate_markov_text(self, transitions, n_syllables, seed_word=None, metre_pattern=None):
        if seed_word is None:
            seed_word = choice(list(transitions.keys()), 1)[0]
        prev_step = seed_word
        text = seed_word
        syllables_count = len(Phonetics.get_word_syllables(seed_word))

        while syllables_count < n_syllables:
            if transitions.get(prev_step) is not None:
                transition = transitions[prev_step]

                transition = self.filter_transition(transition, metre_pattern,
                                                    n_syllables-syllables_count, syllables_count)
                if len(transition) == 0:
                    return ""

                candidates = list(transition.keys())
                weights = list(transition.values())
                weights = [w / sum(weights) for w in weights]
                next_word = self.words_short[choice(candidates, 1, p=weights)[0]]
                next_text = next_word.text.lower()
            else:
                return ""

            prev_step = next_text
            text += " " + next_text
            syllables_count += len(Phonetics.get_word_syllables(next_text))
        return text

    def filter_rhyme_candidates(self, rhyme_candidates, metre_pattern):
        rhyming_word_ending = metre_pattern[-2:]
        filtered_rhyme_candidates = {}
        for short, val in rhyme_candidates.items():
            rhyme = self.words_short[short]
            if len(rhyme.syllables) < 2:
                continue
            bad_word = False
            for i in range(2):
                syllable = rhyme.syllables[-1-i]
                if syllable.accent != -1 and rhyming_word_ending[-1 - i] == "-":
                    bad_word = True
            if not bad_word:
                filtered_rhyme_candidates[short] = val
        return filtered_rhyme_candidates

    def generate_poem(self, metre_schema="-+", rhyme_schema="abab", n_lines=8, n_syllables=8):
        metre_pattern = ""
        while len(metre_pattern) < n_syllables:
            metre_pattern += metre_schema
        metre_pattern = metre_pattern[:n_syllables]

        if n_lines % len(rhyme_schema) != 0:
            return "Wrong params"

        n_parts = n_lines // len(rhyme_schema)
        poem = ""
        unique_letters = list(set(list(rhyme_schema)))
        rhyme_candidates = list(self.filter_rhyme_candidates(self.rhymes, metre_pattern).keys())

        for i in range(n_parts):
            letter_all_rhymes = {}
            for letter in unique_letters:
                letter_all_rhymes[letter] = []
                while len(letter_all_rhymes[letter]) < rhyme_schema.count(letter):
                    seed_rhyme = choice(rhyme_candidates, 1)[0]
                    rhyme_with_seed = set(self.filter_rhyme_candidates(self.rhymes[seed_rhyme], metre_pattern))
                    rhyme_with_seed.add(seed_rhyme)
                    letter_all_rhymes[letter] = list(rhyme_with_seed)

            for letter in rhyme_schema:
                generated = ""
                i = 0
                while generated == "" and i < 20:
                    i += 1
                    seed = self.words_short[choice(letter_all_rhymes[letter], 1)[0]]
                    generated = self.generate_markov_text(self.transitions_inverse, n_syllables,
                                                          seed_word=seed.text.lower(), metre_pattern=metre_pattern)
                    if generated != "":
                        letter_all_rhymes[letter].remove(seed.get_short())

                if generated == "":
                    print("Retry")
                    return self.generate_poem(metre_schema, rhyme_schema, n_lines, n_syllables)

                line = " ".join(reversed(generated.split(" ")))
                poem += line + "\n"
        return poem
