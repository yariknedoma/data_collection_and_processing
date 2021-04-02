# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst


# данные характеристик товара изначально собираются в плохом виде
def normalize_definitions(data):
    try:
        data = data.split('\n')[1][16:]
    except Exception as e:
        print(e)
    return data


def price_int_convert(price):
    try:
        price = int(price.replace(' ', ''))
    except Exception as e:
        print(e)
    return price


class Lesson7ScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    details_names = scrapy.Field()
    details_definitions = scrapy.Field(output_processor=MapCompose(normalize_definitions))
    details = scrapy.Field()
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(price_int_convert), output_processor=TakeFirst())

