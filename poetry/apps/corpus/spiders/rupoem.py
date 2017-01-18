# -*- coding: utf-8 -*- s
import scrapy
import re


class RupoemSpider(scrapy.Spider):
    name = 'poems_klassika'
    not_themes = ["Серебряный век", "Советские", "Короткие", "Баллады", "Басни", "Песни",
                  "Лирические", "Школьная программа", "Популярные"]
    start_urls = ['http://rupoem.ru']
    custom_settings = {}

    def parse(self, response):
        for href in response.css('.menuAuthor a::attr(href)'):
            poet_url = response.urljoin(href.extract())
            yield scrapy.Request(poet_url, callback=self.parse_poet)

    def parse_poet(self, response):
        for href in response.css('.catlink a::attr(href)'):
            poem_url = response.urljoin(href.extract())
            yield scrapy.Request(poem_url, callback=self.parse_poem)

    def parse_poem(self, response):
        name = response.css('.poemtitle::text').extract_first()
        text = "".join(response.xpath('//div[@class="poem-text"]//text()[not(ancestor::sup)]').extract())
        themes = response.xpath('//h4/following-sibling::a/text()').extract()
        themes = [theme for theme in themes if theme not in self.not_themes]
        author = response.xpath('//td[@class="topmenu"]//span/a/text()').extract()[1]
        dates = []
        dates_string = response.css('.poemyear::text').extract_first()
        if dates_string is not None:
            dates = re.findall("1[0-9]{3}", dates_string)
        result = {
            'author': " ".join(author.strip().split()),
            'text': text
        }
        if name != "* * *":
            result['name'] = " ".join(name.strip().split())
        if len(dates) != 0:
            result['date_from'] = dates[0]
            result['date_to'] = dates[-1]
        if len(themes) != 0:
            result['themes'] = themes
        yield result
