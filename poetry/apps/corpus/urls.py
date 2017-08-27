from django.conf.urls import url, include

from poetry.apps.corpus.views.comparison_view import ComparisonView
from poetry.apps.corpus.views.poem_list_view import PoemsListView
from poetry.apps.corpus.views.markup_view import MarkupView
from poetry.apps.corpus.views.version_list_view import MarkupVersionListView

urlpatterns = [
    url(r'^poems/', PoemsListView.as_view(), name='poems'),
    url(r'^versions/', MarkupVersionListView.as_view(), name='versions'),
    url(r'^markups/(?P<pk>[0-9]*)/$', MarkupView.as_view(), name="markup"),
    url(r'^search/', include('haystack.urls', namespace="search")),
    url(r'^comparison/$', ComparisonView.as_view(), name="comparison"),
]
