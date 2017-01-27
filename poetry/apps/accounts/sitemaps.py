from django.contrib.sitemaps import GenericSitemap, Sitemap
from django.urls import reverse


class AccountsStaticSitemap(Sitemap):
    priority = 0.5

    def items(self):
        return ['signup', 'login']

    def location(self, item):
        return reverse(item)
