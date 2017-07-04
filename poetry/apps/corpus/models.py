import jsonpickle

from django.core.urlresolvers import reverse
from django.db.models import Model, CharField, IntegerField, TextField, ManyToManyField, ForeignKey, \
    DateTimeField, BooleanField

from rupo.main.markup import Markup as InternalMarkup


class Theme(Model):
    theme = CharField("Тема", max_length=50, blank=False)

    def __str__(self):
        return 'Тема: ' + str(self.theme)

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"


class Poem(Model):
    text = TextField("Текст", blank=False)
    name = CharField("Нвзвание стихотворения", max_length=50, blank=True)
    author = CharField("Автор", max_length=50, blank=False)
    date_from = IntegerField("Дата написания - первый год", blank=True, null=True)
    date_to = IntegerField("Дата написания - второй год", blank=True, null=True)
    themes = ManyToManyField(Theme, verbose_name="Темы", related_name="poems", blank=True)
    is_restricted = BooleanField("Стихи с ограниченным доступом", default=False)

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

    def count_lines(self):
        return len(self.text.rstrip().split("\n"))

    def count_automatic_errors(self):
        for markup in self.markup_instances.all():
            if markup.author == "Automatic":
                return markup.get_automatic_additional().get_metre_errors_count()

    def get_absolute_url(self):
        if len(self.markup_instances.all()) != 0:
            return self.markup_instances.all()[0].get_absolute_url()
        return reverse("corpus:poems")

    def get_automatic_markup(self):
        for markup in self.markup_instances.all():
            if markup.author == "Automatic":
                return markup
        return None

    def count_manual_markups(self):
        return sum([int(markup.author != "Automatic") for markup in self.markup_instances.all()])

    class Meta:
        verbose_name = "Стихотворение"
        verbose_name_plural = "Стихотворения"
        permissions = (
            ("can_view_restricted_poems", "Can view restricted poems"),
        )


class Markup(Model):
    name = CharField("Имя разметки", max_length=50, blank=False)
    additional = TextField("Дополнительная ифнормация", blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Разметка"
        verbose_name_plural = "Разметки"


class MarkupInstance(Model):
    poem = ForeignKey(Poem, related_name="markup_instances")
    text = TextField("Слоговая разметка по ударениям", blank=True, default="")
    author = CharField("Автор разметки", max_length=50, blank=False)
    additional = TextField("Дополнительная ифнормация", blank=True)
    markup = ForeignKey(Markup, related_name="instances")

    def __str__(self):
        return 'Экземпляр разметки' + str(self.poem.name) + " " + str(self.author)

    def get_absolute_url(self):
        return reverse("corpus:markup", kwargs={"pk": self.pk})

    def get_markup(self):
        markup = InternalMarkup()
        markup.from_json(self.text)
        return markup

    def get_automatic_additional(self):
        if self.additional:
            clf = jsonpickle.decode(self.additional)
            return clf
        else:
            return ""

    class Meta:
        verbose_name = "Экзепляр разметки"
        verbose_name_plural = "Экзепляры разметки"


class GenerationSettings(Model):
    metre_schema = TextField("Схема метра", blank=False, default="+-")
    syllables_count = IntegerField("Количество слогов", blank=False, default=8)
    rhyme_schema = TextField("Схема рифмовки", blank=False, default="aabb")
    line = TextField("Первая строчка", blank=True, default="")

    def __str__(self):
        return 'Настройки генерации: ' + str(self.metre_schema) + " " + \
               str(self.syllables_count) + " " + str(self.rhyme_schema)

    class Meta:
        verbose_name = "Набор настроек генерации"
        verbose_name_plural = "Наборы настроек генерации"


class AutomaticPoem(Model):
    text = TextField("Текст", blank=False)
    date = DateTimeField("Дата и время генерации")
    settings = ForeignKey(GenerationSettings, related_name="poems", verbose_name="Настройки")

    def __str__(self):
        return 'Сгенерированное стихотворение ' + str(self.date)

    class Meta:
        verbose_name = "Сгенерированное стихотворение"
        verbose_name_plural = "Сгенерированные стихотворения"
