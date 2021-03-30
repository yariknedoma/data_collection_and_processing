# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Lesson6ScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    salary = scrapy.Field()
    min = scrapy.Field()
    max = scrapy.Field()
    currency = scrapy.Field()
    link = scrapy.Field()
    source = scrapy.Field()
    _id = scrapy.Field()
