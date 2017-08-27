from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View
from django.http import HttpResponse
from braces.views import LoginRequiredMixin, GroupRequiredMixin

from poetry.apps.corpus.models import MarkupVersion


class MarkupVersionExportView(LoginRequiredMixin, GroupRequiredMixin, SingleObjectMixin, View):
    model = MarkupVersion
    group_required = "Approved"

    def get(self, request, *args, **kwargs):
        version = self.get_object()
        response = HttpResponse()
        content = "["
        for markup in version.markups.all():
            content += markup.text + ","
        content = content[:-1] + "]"
        response.content = content
        response["Content-Disposition"] = "attachment; filename={0}".format(version.name + ".json")
        return response