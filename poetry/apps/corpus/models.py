from django.db.models import Model, CharField, IntegerField, TextField, ManyToManyField, ForeignKey, DateTimeField


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

    def count_manual_markups(self):
        return sum([int(markup.author != "Automatic") for markup in self.markups.all()])

    class Meta:
        verbose_name = "Стихотворение"
        verbose_name_plural = "Стихотворения"


class Markup(Model):
    poem = ForeignKey(Poem, related_name="markups")
    text = TextField("Слоговая разметка по ударениям", blank=True, default="")
    author = CharField("Автор разметки", max_length=50, blank=False)
    additional = TextField("Дополнительная ифнормация", blank=True)

    def __str__(self):
        return 'Разметка' + str(self.poem.name) + " " + str(self.author)

    class Meta:
        verbose_name = "Разметка"
        verbose_name_plural = "Разметки"


class GenerationSettings(Model):
    metre_schema = TextField("Схема метра", blank=False, default="+-")
    syllables_count = IntegerField("Количество слогов", blank=False, default=8)
    rhyme_schema = TextField("Схема рифмовки", blank=False, default="aabb")

    def __str__(self):
        return 'Настройки генерации: ' + str(self.metre_schema) + " " + \
               str(self.syllables_count) + " " + str(self.rhyme_schema)

    class Meta:
        verbose_name = "Набор настроек генерации"
        verbose_name_plural = "Наборы настроек генерации"


class AutomaticPoem(Model):
    text = TextField("Текст", blank=False)
    date = DateTimeField("Дата и время генерации")
    settings = ForeignKey(GenerationSettings, related_name="settings", verbose_name="Настройки")

    def __str__(self):
        return 'Сгенерированное стихотворение ' + str(self.date)

    class Meta:
        verbose_name = "Сгенерированное стихотворение"
        verbose_name_plural = "Сгенерированные стихотворения"
