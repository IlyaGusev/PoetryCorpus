from django.contrib.sitemaps import GenericSitemap
from poetry.apps.corpus.models import Poem


class CorpusDataSitemap(GenericSitemap):
    priority = 0.9

    def __init__(self):
        super(CorpusDataSitemap, self).__init__(info_dict={'queryset': Poem.objects.all()})