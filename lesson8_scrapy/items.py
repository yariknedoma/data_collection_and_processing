# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Lesson8ScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    full_name = scrapy.Field()
    user_id = scrapy.Field()
    username = scrapy.Field()
    photo = scrapy.Field()
    profile_owner = scrapy.Field()
    follower = scrapy.Field()
    data = scrapy.Field()
    being_scraped = scrapy.Field()
    _id = scrapy.Field()

