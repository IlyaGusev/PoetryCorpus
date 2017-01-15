from django.conf.urls import url

from poetry_corpus.apps.corpus.views import PoemsListView, PoemView, MarkupView, GeneratorView

urlpatterns = [
    url(r'^poems/$', PoemsListView.as_view(), name='poems'),
    url(r'^poems/(?P<pk>[0-9]*)/$', PoemView.as_view(), name="poem"),
    url(r'^generator/$', GeneratorView.as_view(), name="generator"),
    url(r'^markups/(?P<pk>[0-9]*)/$', MarkupView.as_view(), name="markup"),
]
