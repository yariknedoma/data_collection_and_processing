import scrapy
from scrapy.http import HtmlResponse
from lesson7_scrapy.items import Lesson7ScrapyItem
from scrapy.loader import ItemLoader


class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, query):
        super(LeroymerlinruSpider, self).__init__()

        self.start_urls = [f'https://leroymerlin.ru/search/?q={query}']

    def parse(self, response:HtmlResponse):
        links = response.xpath("//a[@slot='name']")
        for link in links:
            yield response.follow(link, callback=self.parse_item)
        next_page = response.xpath("//a[contains(@class, 'next-paginator-button')]")
        if next_page:
            next_page = next_page[0]
            yield response.follow(next_page, callback=self.parse)

    def parse_item(self, response:HtmlResponse):
        loader = ItemLoader(item=Lesson7ScrapyItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('photos', "//picture[@slot='pictures']/img/@src")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('details_names', "//dt[@class='def-list__term']/text()")
        loader.add_xpath('details_definitions', "//dd[@class='def-list__definition']/text()")
        loader.add_value('link', response.url)
        return loader.load_item()