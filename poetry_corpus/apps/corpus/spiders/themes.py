# -*- coding: utf-8 -*- s
import scrapy
import re

themes_to_unique = {
    'Стихи на военную тему': 'Военные',
    'Стихи о дружбе': 'О дружбе',
    'Стихи о любви': 'О любви',
    'Стихи о России': 'Патриотические'
}


class ThemeSpider(scrapy.Spider):
    name = 'poems_theme'
    start_urls = ['http://strofa.su/temy/o-rodine/', 'http://strofa.su/temy/o-druzhbe/',
    'http://strofa.su/temy/o-vojne/', 'http://strofa.su/temy/o-lubvi/']
    custom_settings = {}

    def parse(self, response):
        theme = response.css('.poemlinks h1::text').extract_first()
        poems = []
        authors = []
        for text in response.css('.poemlinks ul li a::text').extract():
            poems.append(text)
        for text in response.css('.poemlinks ul li span::text').extract():
            authors.append(text)
        for i in range(len(poems)):
            yield {'name': poems[i], 'author': authors[i], 'themes': [themes_to_unique[theme],]}
           

