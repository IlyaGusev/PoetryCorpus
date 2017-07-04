from django.contrib import admin
from reversion.admin import VersionAdmin

from poetry.apps.corpus.models import Poem, Theme, MarkupInstance, AutomaticPoem, GenerationSettings, Markup


class PoemInline(admin.StackedInline):
    model = Poem.themes.through


@admin.register(Poem)
class PoemAdmin(VersionAdmin):
    model = Poem


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    model = Theme
    inlines = [PoemInline, ]


@admin.register(MarkupInstance)
class MarkupInstanceAdmin(VersionAdmin):
    model = MarkupInstance


@admin.register(AutomaticPoem)
class AutomaticPoemAdmin(VersionAdmin):
    model = AutomaticPoem


@admin.register(GenerationSettings)
class GenerationSettingsAdmin(VersionAdmin):
    model = GenerationSettings


@admin.register(Markup)
class MarkupAdmin(VersionAdmin):
    model = Markup

