from django.conf.urls import url, include

from poetry.apps.corpus.views import PoemsListView, MarkupView, GeneratorView

urlpatterns = [
    url(r'^poems/', PoemsListView.as_view(), name='poems'),
    url(r'^generator/$', GeneratorView.as_view(), name="generator"),
    url(r'^markups/(?P<pk>[0-9]*)/$', MarkupView.as_view(), name="markup"),
    url(r'^search/', include('haystack.urls', namespace="search")),
]
