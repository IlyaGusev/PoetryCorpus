from django.forms import ModelForm
from django.shortcuts import get_object_or_404

from poetry.apps.corpus.models import Poem


class OverwriteOnlyModelFormMixin(object):
    """
    Delete POST keys that were not actually found in the POST dict
    to prevent accidental overwriting of fields due to missing POST data.
    Mixin для поддержки перезаписи полей. Без него незаполенные поля считаются пустыми.
    """
    def __init__(self, *args, **kwargs):
        super(OverwriteOnlyModelFormMixin, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].required = False

    def clean(self):
        cleaned_data = super(OverwriteOnlyModelFormMixin, self).clean()
        # Записываем в data новые поля
        data = {}
        for field in cleaned_data.keys():
            if field in self.data:
                data[field] = cleaned_data[field]
        # Запоминаем новые поля
        obj = get_object_or_404(self._meta.model, pk=self.instance.pk)
        # Достаём старые поля и обновляем их
        model_data = obj.__dict__
        model_data.update(data)
        return model_data


class PoemForm(OverwriteOnlyModelFormMixin, ModelForm):
    class Meta:
        model = Poem
        fields = ('author', 'name', 'text')