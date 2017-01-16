import scrapy
import re


class StrofaSpider(scrapy.Spider):
    name = 'poems_klassika'
    start_urls = ['http://www.klassika.ru/stihi/']
    custom_settings = {}

    def parse(self, response):
        for href in response.xpath('//div[@id="margins"]/a[contains(@href, "/stihi")]/@href'):
            poet_url = response.urljoin(href.extract())
            yield scrapy.Request(poet_url, callback=self.parse_poet)

    def parse_poet(self, response):
        for href in response.css('body ul li a::attr(href)'):
            poem_url = response.urljoin(href.extract())
            yield scrapy.Request(poem_url, callback=self.parse_poem)

    def parse_poem(self, response):
        name = response.css('#title::text').extract_first()
        if name is None:
            name = response.css('pre i').extract_first()
        text = "\n".join(response.css('#margins pre::text').extract())
        author = response.css('h1 em a::text').extract_first()
        dates = []
        dates_string = response.xpath('//div[@id="margins"]/font[contains(@size, "2")]/text()').extract_first()
        if dates_string is not None:
            dates = re.findall("1[0-9]{3}", dates_string)
        result = {
            'author': " ".join(author.strip().split()),
            'text': text
        }
        if " ".join(name.strip().split()) != "* * *":
            result['name'] = " ".join(name.strip().split())
        if len(dates) != 0:
            result['date_from'] = dates[0]
            result['date_to'] = dates[-1]
        yield result
