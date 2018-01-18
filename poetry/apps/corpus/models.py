import jsonpickle

from django.core.urlresolvers import reverse
from django.db.models import Model, CharField, IntegerField, TextField, ManyToManyField, ForeignKey, BooleanField

from rupo.main.markup import Markup as InternalMarkup
from rupo.metre.metre_classifier import StressCorrection


class Theme(Model):
    name = CharField("Тема", max_length=50, blank=False)

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"

    def __str__(self):
        return 'Тема: ' + str(self.name)


class Poem(Model):
    text = TextField("Текст", blank=False)
    name = CharField("Нвзвание стихотворения", max_length=50, blank=True)
    author = CharField("Автор", max_length=50, blank=False)
    date_from = IntegerField("Дата написания - первый год", blank=True, null=True)
    date_to = IntegerField("Дата написания - второй год", blank=True, null=True)
    themes = ManyToManyField(Theme, verbose_name="Темы", related_name="poems", blank=True)
    is_restricted = BooleanField("Стихи с ограниченным доступом", default=False)
    is_standard = BooleanField("Эталонные (проверенные) стихи", default=False)

    class Meta:
        verbose_name = "Стихотворение"
        verbose_name_plural = "Стихотворения"
        permissions = (
            ("can_view_restricted_poems", "Can view restricted poems"),
        )

    def __str__(self):
        return 'Стихотворение: ' + self.get_name() + ", " + str(self.author)

    def get_name(self):
        name = self.name
        if name == "":
            name = self.text.strip().split("\n")[0]
            i = len(name) - 1
            while i > 0 and not name[i].isalpha():
                i -= 1
            name = name[:i+1]
        return name

    def get_name_short(self):
        name = self.__clean_name(self.name)
        if name == "":
            name = self.__get_name_form_text()
        return name[:64].replace(" ", "")

    def __get_name_form_text(self):
        name = ""
        line_number = 0
        while name == "":
            name = self.text.strip().split("\n")[line_number]
            i = len(name) - 1
            while i > 0 and not name[i].isalpha():
                i -= 1
            name = name[:i+1]
            name = self.__clean_name(name)
            line_number += 1
        return name

    def __clean_name(self, name):
        new_name = ""
        for ch in name:
            if ch.isalpha() or ch.isalnum() or ch == " ":
                new_name += ch
        return new_name.strip()

    def count_lines(self):
        return len(self.text.rstrip().split("\n"))

    def count_automatic_errors(self):
        for markup in self.markups.all():
            if "Automatic" in markup.author:
                return markup.get_automatic_additional().get_metre_errors_count()

    def get_absolute_url(self):
        if len(self.markups.all()) != 0:
            return self.markups.all()[0].get_absolute_url()
        return reverse("corpus:poems")

    def get_automatic_markup(self):
        for markup in self.markups.all():
            if "Automatic" in markup.author:
                return markup
        return None

    def count_manual_markups(self):
        return sum([int(markup.markup_version.name == "Manual") for markup in self.markups.all()])


class MarkupVersion(Model):
    name = CharField("Имя версии разметки", max_length=50, blank=False)
    additional = TextField("Дополнительная ифнормация", blank=True)
    is_manual = BooleanField("Ручные разметки?", default=False)

    class Meta:
        verbose_name = "Версия разметки"
        verbose_name_plural = "Версии разметки"

    def __str__(self):
        return str(self.name)

    def count_markups(self):
        return self.markups.count()


class Markup(Model):
    poem = ForeignKey(Poem, related_name="markups")
    data = TextField("Слоговая разметка по ударениям", blank=True, default="")
    author = CharField("Автор разметки", max_length=50, blank=False)
    additional = TextField("Дополнительная ифнормация", blank=True)
    markup_version = ForeignKey(MarkupVersion, related_name="markups")
    is_standard = BooleanField("Эталонная (проверенная) разметка", default=False)

    class Meta:
        verbose_name = "Экзепляр разметки"
        verbose_name_plural = "Экзепляры разметки"

    def __str__(self):
        return 'Разметка' + str(self.poem.name) + " " + str(self.markup_version) + " " + str(self.author)

    def get_absolute_url(self):
        return reverse("corpus:markup", kwargs={"pk": self.pk})

    def get_markup(self):
        markup = InternalMarkup()
        markup.from_json(self.data)
        return markup

    def get_automatic_additional(self):
        if self.additional:
            clf = jsonpickle.decode(self.additional)
            a = list([a for l in clf.corrections.values() for a in l]) + \
                list([a for l in clf.additions.values() for a in l]) + \
                list([a for l in clf.resolutions.values() for a in l])
            if len(a) != 0 and type(a[0]) is not StressCorrection:
                self.__compatibility_stress_correction(clf.corrections)
                self.__compatibility_stress_correction(clf.resolutions)
                self.__compatibility_stress_correction(clf.additions)
            return clf
        else:
            return ""

    def __compatibility_stress_correction(self, collection):
        for key, value in collection.items():
            new_value = []
            for info in value:
                new_value.append(StressCorrection(info['line_number'], info["word_number"],
                                                  info["syllable_number"], info["word_text"], info["accent"]))
            collection[key] = new_value