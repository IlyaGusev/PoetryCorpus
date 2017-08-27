from collections import namedtuple
from typing import List

from django.views.generic import TemplateView, View
from django.http import HttpResponse
from braces.views import LoginRequiredMixin, GroupRequiredMixin

from poetry.apps.corpus.models import Poem, MarkupVersion
from rupo.main.markup import Markup


def get_accents(markup: Markup):
    accents = []
    for line in markup.lines:
        for word in line.words:
            for syllable in word.syllables:
                accents.append(syllable.stress != -1)
    return accents


def get_accuracy(standard_accents: List[bool], test_accents: List[bool]):
    l = min(len(standard_accents), len(test_accents))
    hits = sum([1 for standard_accent, test_accent in zip(standard_accents, test_accents)
                if standard_accent == test_accent])
    return float(hits) / l


def get_precision(standard_accents: List[bool], test_accents: List[bool]):
    tp = sum([1 for standard_accent, test_accent in zip(standard_accents, test_accents)
              if standard_accent == test_accent == 1])
    tp_fp = sum([1 for accent in test_accents if accent == 1])
    return float(tp) / tp_fp


def get_recall(standard_accents: List[bool], test_accents: List[bool]):
    tp = sum([1 for standard_accent, test_accent in zip(standard_accents, test_accents)
              if standard_accent == test_accent == 1])
    tp_fn = sum([1 for accent in standard_accents if accent == 1])
    return float(tp) / tp_fn


def get_comparison(poem, standard_pk, test_pk):
    test_markup = None
    standard_markup = None
    for markup in poem.markups.all():
        if markup.markup_version.pk == standard_pk:
            standard_markup = markup
        if markup.markup_version.pk == test_pk:
            test_markup = markup
    assert test_markup.get_markup().text == standard_markup.get_markup().text
    standard_accents = get_accents(standard_markup.get_markup())
    test_accents = get_accents(test_markup.get_markup())
    accuracy = get_accuracy(standard_accents, test_accents)
    precision = get_precision(standard_accents, test_accents)
    recall = get_recall(standard_accents, test_accents)
    f1 = 2*precision*recall/(precision+recall)
    Comparison = namedtuple("Comparison", "poem test standard accuracy precision recall f1")
    return Comparison(poem=poem, test=test_markup, standard=standard_markup, accuracy=accuracy,
                      precision=precision, recall=recall, f1=f1)


def get_all_comparisons(standard_pk, test_pk):
    standard_markup_version = MarkupVersion.objects.get(pk=standard_pk)
    poems = list(set([markup.poem for markup in standard_markup_version.markups.filter(
        poem__markups__markup_version=test_pk)]))
    return [get_comparison(poem, standard_pk, test_pk) for poem in poems]


class ComparisonView(LoginRequiredMixin, GroupRequiredMixin, TemplateView):
    template_name = 'comparison.html'
    group_required = "Approved"

    def get_context_data(self, **kwargs):
        context = super(ComparisonView, self).get_context_data(**kwargs)
        test_pk = int(self.request.GET["test"])
        standard_pk = int(self.request.GET["standard"])
        document_pk = self.request.GET.get("document", None)

        if document_pk is None:
            comparisons = get_all_comparisons(standard_pk, test_pk)
        else:
            comparisons = [get_comparison(Poem.objects.get(pk=document_pk), standard_pk, test_pk)]
        context["comparisons"] = comparisons
        context["avg_accuracy"] = sum([comparison.accuracy for comparison in comparisons])/len(comparisons)
        context["avg_f1"] = sum([comparison.f1 for comparison in comparisons]) / len(comparisons)
        return context


class ComparisonCSVView(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = "Approved"

    def get(self, request, *args, **kwargs):
        standard_pk = int(request.GET["standard"])
        test_pk = int(request.GET["test"])
        response = HttpResponse()
        comparisons = get_all_comparisons(standard_pk, test_pk)
        content = "poem,test,standard,accuracy,precision,recall,f1\n"
        for comparison in comparisons:
            content += ",".join([comparison.poem.name.replace(",", ""),
                                 comparison.test.author.replace(",", ""),
                                 comparison.standard.author.replace(",", ""),
                                 "{:.3f}".format(comparison.accuracy),
                                 "{:.3f}".format(comparison.precision),
                                 "{:.3f}".format(comparison.recall),
                                 "{:.3f}".format(comparison.f1)]) + "\n"
        response.content = content
        response["Content-Disposition"] = "attachment; filename={0}".format(
            "comparison" + str(standard_pk) + "-" + str(test_pk) + ".csv")
        return response
