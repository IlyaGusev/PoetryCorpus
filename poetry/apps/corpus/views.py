from rest_framework import viewsets
from poetry.apps.corpus.serializers import PoemSerializer, MarkupVersionSerializer, MarkupSerializer
from poetry.apps.corpus.models import Poem, MarkupVersion, Markup


class PoemViewSet(viewsets.ModelViewSet):
    queryset = Poem.objects.all()
    serializer_class = PoemSerializer


class MarkupVersionViewSet(viewsets.ModelViewSet):
    queryset = MarkupVersion.objects.all()
    serializer_class = MarkupVersionSerializer


class MarkupViewSet(viewsets.ModelViewSet):
    queryset = Markup.objects.all()
    serializer_class = MarkupSerializer
