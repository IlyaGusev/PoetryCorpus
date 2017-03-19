from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from poetry.apps.api.views import GetAccent

urlpatterns = [
    url(r'^accent/', GetAccent.as_view()),
]