from django.conf.urls import url, include

from poetry.apps.corpus.views import PoemsListView, MarkupView, GeneratorView, AnalysisView, AccentsView, RhymesView, \
    DownloadMarkupsView

urlpatterns = [
    url(r'^poems/', PoemsListView.as_view(), name='poems'),
    url(r'^generator/$', GeneratorView.as_view(), name="generator"),
    url(r'^markups/(?P<pk>[0-9]*)/$', MarkupView.as_view(), name="markup"),
    url(r'^accents/$', AccentsView.as_view(), name="accents"),
    url(r'^rhymes/$', RhymesView.as_view(), name="rhymes"),
    url(r'^analysis/$', AnalysisView.as_view(), name="analysis"),
    url(r'^search/', include('haystack.urls', namespace="search")),
    url(r'^download_manual/$', DownloadMarkupsView.as_view(), name="download"),
]
