import scrapy
from scrapy.http import HtmlResponse
from lesson6_scrapy.items import Lesson6ScrapyItem


class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python&noGeo=1']

    def parse(self, response:HtmlResponse):
        links = response.xpath("//a[contains(@class, '_6AfZ9')]/@href").extract()
        links = ['https://www.superjob.ru'+link for link in links]
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)
        next_page = response.css("//a[contains(@class, 'f-test-button-dalshe')]/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacancy_parse(self, response:HtmlResponse):
        vacancy_name = response.xpath('//h1//text()').extract_first()
        vacancy_salary = response.xpath("//span[@class='_3mfro _2Wp8I PlM3e _2JVkc']/text()").extract()
        vacancy_link = response.url
        yield Lesson6ScrapyItem(name=vacancy_name, salary=vacancy_salary, link=vacancy_link)

