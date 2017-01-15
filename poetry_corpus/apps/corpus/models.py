from django.db.models import Model, CharField, IntegerField, TextField, ManyToManyField, BooleanField, ForeignKey


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
        return 'Стихотворение: ' + (str(self.name) if str(self.name) != '' else str(self.text).split('\n')[0]) + \
               ", " + str(self.author)

    class Meta:
        verbose_name = "Стихотворение"
        verbose_name_plural = "Стихотворения"


class Markup(Model):
    poem = ForeignKey(Poem, related_name="markups")
    text = TextField("Слоговая разметка по ударениям", blank=True, default="")
    author = CharField("Автор разметки", max_length=50, blank=False)

    def __str__(self):
        return 'Разметка' + str(self.poem.name) + " " + str(self.author)

    class Meta:
        verbose_name = "Разметка"
        verbose_name_plural = "Разметки"
