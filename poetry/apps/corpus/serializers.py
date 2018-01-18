from rest_framework import serializers
from poetry.apps.corpus.models import Theme, Poem, Markup, MarkupVersion


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ("name", )


class PoemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poem
        fields = ("name", "author", "text", "date_from", "date_to", "themes", "is_restricted", "is_standard")


class MarkupVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkupVersion
        fields = (
            "name", "additional", "is_manual"
        )


class MarkupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Markup
        fields = (
            "poem", "data", "author", "data", "markup_version", "is_standard"
        )