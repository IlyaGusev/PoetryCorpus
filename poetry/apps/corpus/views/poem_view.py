from django.core.urlresolvers import reverse, reverse_lazy
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View, UpdateView, DeleteView

from braces.views import LoginRequiredMixin, GroupRequiredMixin

from poetry.apps.corpus.models import Poem
from poetry.apps.corpus.forms import PoemForm


class PoemView(UpdateView):
    model = Poem
    template_name = 'poem.html'
    context_object_name = 'poem'
    form_class = PoemForm

    def get_context_data(self, **kwargs):
        context = super(PoemView, self).get_context_data(**kwargs)
        poem = self.get_object()
        max_pk = Poem.objects.latest('pk').pk

        next_pk = poem.pk + 1
        while not Poem.objects.filter(pk=next_pk).exists() and next_pk < max_pk:
            next_pk += 1
        if not Poem.objects.filter(pk=next_pk).exists():
            next_pk = None

        prev_pk = poem.pk - 1
        while not Poem.objects.filter(pk=prev_pk).exists() and prev_pk > 0:
            prev_pk -= 1
        if not Poem.objects.filter(pk=prev_pk).exists():
            prev_pk = None
        context['next_pk'] = next_pk if next_pk is not None else poem.pk

        context['prev_pk'] = prev_pk if prev_pk is not None else poem.pk
        context['can_edit'] = self.request.user.is_superuser
        return context


class PoemMakeStandardView(LoginRequiredMixin, GroupRequiredMixin, View, SingleObjectMixin):
    model = Poem
    group_required = "Approved"
    raise_exception = True

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.is_superuser:
            poem = self.get_object()
            poem.is_standard = True
            poem.save()
            return JsonResponse({'url': reverse('corpus:poem', kwargs={'pk': poem.pk}), }, status=200)
        else:
            raise PermissionDenied


class PoemDeleteView(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = Poem
    group_required = "Approved"
    success_url = reverse_lazy('corpus:poems')
    raise_exception = True
