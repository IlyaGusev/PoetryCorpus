from django.views.generic import ListView

from poetry.apps.corpus.models import MarkupVersion


class MarkupVersionListView(ListView):
    model = MarkupVersion
    template_name = 'versions.html'
    context_object_name = 'versions'
    paginate_by = 50
