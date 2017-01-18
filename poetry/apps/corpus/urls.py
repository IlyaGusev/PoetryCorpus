from django.conf.urls import url

from poetry.apps.corpus.views import PoemsListView, MarkupView, GeneratorView

urlpatterns = [
    url(r'^poems/page/(?P<page>[0-9]*)$', PoemsListView.as_view(), name='poems'),
    url(r'^generator/$', GeneratorView.as_view(), name="generator"),
    url(r'^markups/(?P<pk>[0-9]*)/$', MarkupView.as_view(), name="markup"),
]
