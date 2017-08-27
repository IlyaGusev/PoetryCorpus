from django.views.generic import ListView
from braces.views import LoginRequiredMixin, GroupRequiredMixin

from poetry.apps.corpus.models import MarkupVersion


class MarkupVersionListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = MarkupVersion
    template_name = 'versions.html'
    context_object_name = 'versions'
    paginate_by = 50
    group_required = "Approved"
