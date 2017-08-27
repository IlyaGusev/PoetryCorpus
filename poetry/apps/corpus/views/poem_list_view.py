from django.views.generic import ListView

from poetry.apps.corpus.models import Poem


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
