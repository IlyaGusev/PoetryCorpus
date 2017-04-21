import datetime

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import DetailView, ListView, FormView, View

import os
import poetry
from poetry.settings import BASE_DIR
from poetry.apps.corpus.forms import GeneratorForm, AccentsForm, RhymesForm, AnalysisForm
from poetry.apps.corpus.models import Poem, GenerationSettings, AutomaticPoem
from poetry.apps.corpus.scripts.settings import MARKUPS_DUMP_XML_PATH, MARKOV_PICKLE, VOCAB_PICKLE

from rupo.main.markup import Markup, Word, Line
from rupo.main.phonetics import Phonetics
from rupo.util.preprocess import VOWELS
from rupo.api import get_accent, generate_poem_by_line, generate_poem, get_improved_markup, get_word_rhymes


class PoemsListView(ListView):
    model = Poem
    template_name = 'poems.html'
    context_object_name = 'poems'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super(PoemsListView, self).get_context_data(**kwargs)
        poems_list = []
        for poem in context['poems']:
            if not self.request.user.has_perm('corpus.can_view_restricted_poems') and poem.is_restricted:
                continue
            poem.name = poem.get_name()
            poems_list.append(poem)
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
        m.from_json(markup.text)
        context['text'] = process_markup(m)
        context['poem'] = markup.poem
        context['poem'].name = markup.poem.get_name()
        context['lines_count'] = markup.poem.count_lines()
        context['additional'] = markup.get_automatic_additional()
        return context

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            diffs = request.POST.getlist('diffs[]')

            m = self.get_object()
            poem = m.poem
            markup = m.get_markup()

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
            m.text = markup.to_json()
            m.author = request.user.email
            m.poem = poem
            m.save()
            return JsonResponse({'url': reverse('corpus:markup', kwargs={'pk': m.pk}),},
                                status=200)
        else:
            raise PermissionDenied


class GeneratorView(FormView):
    template_name = "generator.html"
    success_url = reverse_lazy('corpus:generator')
    form_class = GeneratorForm

    def get_context_data(self, **kwargs):
        context = super(GeneratorView, self).get_context_data(**kwargs)
        settings, created = GenerationSettings.objects.get_or_create(
            metre_schema=self.request.GET.get('metre_schema', "-+"),
            syllables_count=int(self.request.GET.get('syllables_count', 8)),
            rhyme_schema=self.request.GET.get('rhyme_schema', "aabb"),
            line=self.request.GET.get('line', ""))
        try:
            if settings.line != "":
                context['generated'] = \
                    generate_poem_by_line(MARKUPS_DUMP_XML_PATH, MARKOV_PICKLE, VOCAB_PICKLE,
                                          settings.line,
                                          settings.rhyme_schema)
            else:
                context['generated'] = generate_poem(MARKUPS_DUMP_XML_PATH, MARKOV_PICKLE, VOCAB_PICKLE,
                                                     settings.metre_schema,
                                                     settings.rhyme_schema,
                                                     settings.syllables_count)
        except RuntimeError as e:
            context['generated'] = e
        AutomaticPoem.objects.create(text=context['generated'], date=datetime.datetime.now(), settings=settings)
        return context


class AccentsView(FormView):
    template_name = "accents.html"
    success_url = reverse_lazy("corpus:accents")
    form_class = AccentsForm

    def get_context_data(self, **kwargs):
        context = super(AccentsView, self).get_context_data(**kwargs)
        word = self.request.GET.get('word', "")
        if word != "":
            accent = get_accent(word)
            syllables = Phonetics.get_word_syllables(word)
            for syllable in syllables:
                if syllable.begin <= accent < syllable.end:
                    syllable.accent = accent
            markup_word = Word(0, len(word)-1, word, syllables)
            markup_line = Line(0, len(word)-1, word, [markup_word])
            markup = Markup(word, [markup_line])
            context['word_markup'] = process_markup(markup)
        return context


class RhymesView(FormView):
    template_name = "rhymes.html"
    success_url = reverse_lazy("corpus:rhymes")
    form_class = RhymesForm

    def get_context_data(self, **kwargs):
        context = super(RhymesView, self).get_context_data(**kwargs)
        word = self.request.GET.get('word', "")
        if word != "":
            context['rhymes'] = [w for w in get_word_rhymes(word, VOCAB_PICKLE, MARKUPS_DUMP_XML_PATH)]
        return context


class AnalysisView(FormView):
    template_name = "analysis.html"
    success_url = reverse_lazy("corpus:analysis")
    form_class = AnalysisForm

    def get_context_data(self, **kwargs):
        context = super(AnalysisView, self).get_context_data(**kwargs)
        text = self.request.GET.get('text', "")
        if text == "":
            return context
        markup, result = get_improved_markup(text)
        context['accented_text'] = process_markup(markup)
        context['additional'] = result
        return context


class DownloadMarkupsView(View):
    def get(self, request):
        with open(os.path.join(BASE_DIR, "poetry", "static", "download", "ManualMarkups.json"),
                  "w", encoding='utf-8') as f:
            content = '['
            poems = [poem for poem in Poem.objects.all() if poem.count_manual_markups() != 0]
            markups = []
            for poem in poems:
                for markup in poem.markups.all():
                    if markup.author != "Automatic":
                        markups.append(markup)
                        break
            print(len(markups))
            for markup in markups:
                content += markup.text + ","
            content = content[:-1] + ']'
            f.write(content)
        return HttpResponseRedirect("/static/download/ManualMarkups.json")