import os
import datetime
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views.generic import DetailView, ListView, FormView

import poetry
from poetry.settings import BASE_DIR
from poetry.apps.corpus.forms import GeneratorForm
from poetry.apps.corpus.models import Poem, GenerationSettings, AutomaticPoem
from poetry.apps.corpus.scripts.phonetics.phonetics_markup import Markup
from poetry.apps.corpus.scripts.preprocess import VOWELS
from poetry.apps.corpus.scripts.generate.markov import Markov
from poetry.apps.corpus.scripts.phonetics.accent_classifier import AccentClassifier
from poetry.apps.corpus.scripts.phonetics.accent_dict import AccentDict


class Global:
    accent_dict = AccentDict(os.path.join(BASE_DIR, "datasets", "dicts", "accents_dict.txt"))
    accent_classifier = AccentClassifier(os.path.join(BASE_DIR, "datasets", "models"), accent_dict)
    markov = Markov(accent_dict, accent_classifier)


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
    template_name = 'poems.html'
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


class MarkupView(DetailView):
    model = poetry.apps.corpus.models.Markup
    template_name = 'markup.html'
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

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            diffs = request.POST.getlist('diffs[]')

            m = self.get_object()
            poem = m.poem
            markup = Markup()
            markup.from_xml(m.text)

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

            m = poetry.apps.corpus.models.Markup()
            m.text = markup.to_xml()
            m.author = request.user.email
            m.poem = poem
            m.save()
            return JsonResponse({'url': reverse('corpus:markup', kwargs={'pk': m.pk}),},
                                status=200)
        else:
            raise PermissionDenied


class GeneratorView(FormView):
    template_name = "generator.html"
    success_url = '/generator'
    form_class = GeneratorForm

    def get_context_data(self, **kwargs):
        context = super(GeneratorView, self).get_context_data(**kwargs)
        settings, createdz = GenerationSettings.objects.get_or_create(
            metre_schema=self.request.GET.get('metre_schema', "-+"),
            syllables_count=int(self.request.GET.get('syllables_count', 8)),
            rhyme_schema=self.request.GET.get('rhyme_schema', "aabb"))
        context['generated'] = Global.markov.generate_poem(settings.metre_schema,
                                                    settings.rhyme_schema,
                                                    settings.syllables_count)
        AutomaticPoem.objects.create(text=context['generated'], date=datetime.datetime.now(), settings=settings)
        return context
