import scrapy
import re


class StrofaSpider(scrapy.Spider):
    name = 'poems_strofa'
    start_urls = ['http://strofa.su/vse-poety/']
    custom_settings = {}

    def parse(self, response):
        for href in response.css('.poemlinks a::attr(href)'):
            poet_url = response.urljoin(href.extract())
            yield scrapy.Request(poet_url, callback=self.parse_poet)

    def parse_poet(self, response):
        for href in response.css('.poemlinks a::attr(href)'):
            poem_url = response.urljoin(href.extract())
            yield scrapy.Request(poem_url, callback=self.parse_poem)

    def parse_poem(self, response):
        name = response.css('.poem h1::text').extract_first()
        text = "\n".join(response.css('.poem .related::text').extract())
        meta = response.css('.poem .related p::text').extract_first().split(',')
        author = meta[0]
        dates = re.findall(r"1[0-9]{3}", meta[1]) if len(meta) >= 2 else []
        result = {
            'author': author.strip(),
            'text': text
        }
        if " ".join(name.strip().split()) != "* * *":
            result['name'] = name.strip()
        if len(dates) != 0:
            result['date_from'] = dates[0]
            result['date_to'] = dates[-1]
        yield result


