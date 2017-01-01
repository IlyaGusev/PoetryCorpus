from django.contrib import admin
from reversion.admin import VersionAdmin

from poetry_corpus.models import Poem, Theme, Markup


class PoemInline(admin.StackedInline):
    model = Poem.themes.through


@admin.register(Poem)
class PoemAdmin(VersionAdmin):
    model = Poem


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    model = Theme
    inlines = [PoemInline, ]


@admin.register(Markup)
class MarkupAdmin(VersionAdmin):
    model = Markup
