from django.conf.urls import url, include

from poetry.apps.corpus.views.comparison_view import ComparisonView, ComparisonCSVView
from poetry.apps.corpus.views.poem_list_view import PoemsListView
from poetry.apps.corpus.views.markup_view import MarkupView
from poetry.apps.corpus.views.version_list_view import MarkupVersionListView
from poetry.apps.corpus.views.version_export_view import MarkupVersionExportView
from poetry.apps.corpus.views.poem_view import PoemView

urlpatterns = [
    url(r'^poem_list/', PoemsListView.as_view(), name='poems'),
    url(r'^versions/', MarkupVersionListView.as_view(), name='versions'),
    url(r'^export_version/(?P<pk>[0-9]*)/$', MarkupVersionExportView.as_view(), name='export_version'),
    url(r'^poems/(?P<pk>[0-9]*)/$', PoemView.as_view(), name="poem"),
    url(r'^markups/(?P<pk>[0-9]*)/$', MarkupView.as_view(), name="markup"),
    url(r'^search/', include('haystack.urls', namespace="search")),
    url(r'^comparison/$', ComparisonView.as_view(), name="comparison"),
    url(r'^comparison_csv/$', ComparisonCSVView.as_view(), name="comparison_csv"),
]
