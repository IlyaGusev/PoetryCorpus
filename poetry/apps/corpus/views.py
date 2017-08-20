from collections import namedtuple

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views.generic import DetailView, ListView, TemplateView

import poetry
from poetry.apps.corpus.models import Poem, MarkupInstance

from rupo.main.markup import Markup
from rupo.util.preprocess import VOWELS


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
    model = poetry.apps.corpus.models.MarkupInstance
    template_name = 'markup.html'
    context_object_name = 'markup'

    def get_context_data(self, **kwargs):
        context = super(MarkupView, self).get_context_data(**kwargs)
        markup_instance = self.get_object()
        m = Markup()
        m.from_json(markup_instance.text)
        context['text'] = process_markup(m)
        context['poem'] = markup_instance.poem
        context['poem'].name = markup_instance.poem.get_name()
        context['lines_count'] = markup_instance.poem.count_lines()
        context['additional'] = markup_instance.get_automatic_additional()
        markups = set()
        for markup_instance in markup_instance.poem.markup_instances.all():
            markups.add(markup_instance.markup)
        context['markups'] = list(markups)
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

            m = MarkupInstance()
            m.text = markup.to_json()
            m.author = request.user.email
            m.poem = poem
            m.markup = poetry.apps.corpus.models.Markup.objects.get(name="Manual")
            m.save()
            return JsonResponse({'url': reverse('corpus:markup', kwargs={'pk': m.pk}),},
                                status=200)
        else:
            raise PermissionDenied


def get_accents(markup: Markup):
    accents = []
    for line in markup.lines:
        for word in line.words:
            for syllable in word.syllables:
                accents.append(syllable.accent != -1)
    return accents


def compare_markups(test_markup: Markup, standard_markup: Markup):
    assert test_markup.text == standard_markup.text
    test_accents = get_accents(test_markup)
    standard_accents = get_accents(standard_markup)
    assert len(test_accents) == len(standard_accents)
    l = len(standard_accents)
    hits = 0
    for standard_accent, test_accent in zip(standard_accents, test_accents):
        hits += 1 if standard_accent == test_accent else 0
    accuracy = float(hits) / l
    return accuracy


def get_comparison(poem, standard_pk, test_pk):
    test_instance = None
    standard_instance = None
    for markup_instance in poem.markup_instances.all():
        if markup_instance.markup.pk == standard_pk:
            standard_instance = markup_instance
        if markup_instance.markup.pk == test_pk:
            test_instance = markup_instance
    accuracy = compare_markups(test_instance.get_markup(), standard_instance.get_markup())
    Comparison = namedtuple("Comparison", "poem test standard accuracy")
    return Comparison(poem=poem, test=test_instance, standard=standard_instance, accuracy=accuracy)


class ComparisonView(TemplateView):
    template_name = 'comparison.html'

    def get_context_data(self, **kwargs):
        context = super(ComparisonView, self).get_context_data(**kwargs)
        test_pk = int(self.request.GET["test"])
        standard_pk = int(self.request.GET["standard"])
        document_pk = self.request.GET.get("document", None)

        if document_pk is None:
            standard_markup = poetry.apps.corpus.models.Markup.objects.get(pk=standard_pk)
            poems = [instance.poem for instance in standard_markup.instances.filter(poem__markup_instances__markup=test_pk)]
            comparisons = [get_comparison(poem, standard_pk, test_pk) for poem in poems]
        else:
            comparisons = [get_comparison(Poem.objects.get(pk=document_pk), standard_pk, test_pk)]
        context["comparisons"] = comparisons
        context["avg"] = sum([comparison.accuracy for comparison in comparisons])/len(comparisons)
        return context
