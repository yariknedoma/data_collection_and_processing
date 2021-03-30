from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from lesson6_scrapy import settings
from lesson6_scrapy.spiders.hhru import HhruSpider
from lesson6_scrapy.spiders.superjob import SuperjobSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HhruSpider)
    process.crawl(SuperjobSpider)

    process.start()
