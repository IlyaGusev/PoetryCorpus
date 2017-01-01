import os

from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views.generic import DetailView, ListView, TemplateView
from django.core.exceptions import PermissionDenied

import poetry_corpus
from poetry_corpus.settings import BASE_DIR
from poetry_corpus.models import Poem
from poetry_corpus.scripts.preprocess import VOWELS
from poetry_corpus.scripts.phonetics.accent_classifier import AccentClassifier
from poetry_corpus.scripts.phonetics.accent_dict import AccentDict
from poetry_corpus.scripts.phonetics.phonetics_markup import Markup
from poetry_corpus.scripts.phonetics.phonetics import Phonetics
from poetry_corpus.scripts.metre.metre_classifier import MetreClassifier
from poetry_corpus.scripts.generate.markov import Markov

accents_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict.txt"))
accents_classifier = AccentClassifier(os.path.join(BASE_DIR, "datasets", "models"), accents_dict)
markov = Markov()
for poem in Poem.objects.all()[:]:
    markov.add_text(str(poem.text))


def get_name(poem):
    if poem.name == "":
        name = poem.text.strip().split("\n")[0]
        i = len(name) - 1
        while i > 0 and not name[i].isalpha():
            i -= 1
        name = name[:i+1]
    else:
        name = poem.name
    return name


class PoemsListView(ListView):
    model = Poem
    template_name = 'index.html'
    context_object_name = 'poems'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super(PoemsListView, self).get_context_data(**kwargs)
        for i in range(len(context['poems'])):
            context['poems'][i].name = get_name(context['poems'][i])
        return context


def process_markup(markup):
    text = markup.text
    output = []
    prev = 0
    for l in range(len(markup.lines)):
        line = markup.lines[l]
        output.append([])
        for w in range(len(line.words)):
            word = line.words[w]
            t = text[prev:word.begin]
            output[-1].append({'word': {'text': t}, 'word_number': -1})
            if len(word.syllables) == 0:
                output[-1].append({'word': {'text': word.text}, 'word_number': w})
            else:
                output[-1].append({'word': {'text': word.text, 'syllables': []}, 'word_number': w})
                accents_count = sum([1 for syllable in word.syllables if syllable.accent != -1])
                for s in range(len(word.syllables)):
                    syllable = word.syllables[s]
                    output[-1][-1]['word']['syllables'].append(
                        {'text': syllable.text, 'accent': syllable.accent,
                         'omography': accents_count > 1, 'no_accent': accents_count == 0})
            prev = word.end
        output[-1].append({'word': {'text': text[prev:line.end]}, 'word_number': -1})
        prev = line.end
    return output


class PoemView(DetailView):
    model = Poem
    template_name = 'poem.html'
    context_object_name = 'poem'

    def get_context_data(self, **kwargs):
        context = super(PoemView, self).get_context_data(**kwargs)
        poem = context['poem']
        context['poem'].name = get_name(poem)

        markups = poem.markups.all()
        context['markups'] = markups

        markup = Phonetics.process_text(poem.text, accents_dict)
        classifier = MetreClassifier(markup, accents_classifier)
        classifier.classify_metre()
        classifier.get_ml_results()
        markup = classifier.get_improved_markup()
        context['text'] = process_markup(markup)
        context['classifier'] = classifier
        metre = classifier.result_metre
        context['omograph_resolutions'] = \
            [(item['word_text'], item['syllable_number']) for item in classifier.omograph_resolutions[metre]]
        context['corrected_accents'] = \
            [(item['word_text'], item['syllable_number']) for item in classifier.corrected_accents[metre]]
        context['after_ml'] = \
            [(item['word_text'], item['syllable_number']) for item in classifier.after_ml]
        context['additions'] = \
            [(item['word_text'], item['syllable_number']) for item in classifier.additions[metre]]

        context['auto'] = True

        return context

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            poem = self.get_object()
            diffs = request.POST.getlist('diffs[]')

            markup = Phonetics.process_text(poem.text, accents_dict)
            classifier = MetreClassifier(markup, accents_classifier)
            classifier.classify_metre()
            classifier.get_ml_results()
            markup = classifier.get_improved_markup()

            for diff in diffs:
                l = int(diff.split('-')[0])
                w = int(diff.split('-')[1])
                s = int(diff.split('-')[2])
                syllable = markup.lines[l].words[w].syllables[s]
                if syllable.accent != -1:
                    syllable.accent = -1
                else:
                    for i in range(len(syllable.text)):
                        if syllable.text[i] in VOWELS:
                            syllable.accent = syllable.begin + i

            m = poetry_corpus.models.Markup()
            m.text = markup.to_xml()
            m.author = request.user.email
            m.poem = poem
            m.save()
            return JsonResponse({'url': reverse('markup', kwargs={'pk': m.pk}), }, status=200)
        else:
            raise PermissionDenied


class MarkupView(DetailView):
    model = poetry_corpus.models.Markup
    template_name = 'poem.html'
    context_object_name = 'markup'

    def get_context_data(self, **kwargs):
        context = super(MarkupView, self).get_context_data(**kwargs)
        markup = self.get_object()
        m = Markup()
        m.from_xml(markup.text)
        context['text'] = process_markup(m)
        context['poem'] = markup.poem
        context['poem'].name = get_name(markup.poem)
        return context


class GeneratorView(TemplateView):
    template_name = "generator.html"

    def get_context_data(self, **kwargs):
        context = super(GeneratorView, self).get_context_data(**kwargs)
        context['generated'] = markov.generate_markov_text()
        print(context['generated'])
        return context
