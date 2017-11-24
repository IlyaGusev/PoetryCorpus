from django.views.generic import DetailView
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

from poetry.apps.corpus.models import Poem


class PoemView(DetailView):
    model = Poem
    template_name = 'poem.html'
    context_object_name = 'poem'

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
        return context

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.is_superuser():
            text = request.POST.get('text')
            poem = self.get_object()
            poem.text = text
            poem.save()
            return JsonResponse({'url': reverse('corpus:poem', kwargs={'pk': poem.pk}),},
                                status=200)
        else:
            raise PermissionDenied