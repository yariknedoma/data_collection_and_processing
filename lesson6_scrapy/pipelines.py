# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import unicodedata


class Lesson6ScrapyPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy2903

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        min, max, currency = self.process_salary(item['salary'], spider.name)
        item['min'] = min
        item['max'] = max
        item['currency'] = currency
        item['source'] = spider.name
        del item['salary']

        collection.insert_one(item)
        return item

    def process_salary(self, salary, spider_name):
        normalized = [unicodedata.normalize('NFKD', i).replace(' ', '') for i in salary]
        if spider_name == 'hhru':
            if len(normalized) != 1:
                if (normalized[0] == 'от') and (normalized[2] == 'до'):
                    min = int(normalized[1])
                    max = int(normalized[3])
                    currency = normalized[5]
                elif normalized[0] == 'от':
                    min = int(normalized[1])
                    max = None
                    currency = normalized[3]
                elif normalized[0] == 'до':
                    max = int(normalized[1])
                    min = None
                    currency = normalized[3]

            else:
                min = max = currency = None

        elif spider_name == 'superjob':
            if len(normalized) != 1:
                if len(normalized) == 4:
                    min = int(normalized[0])
                    max = int(normalized[1])
                    currency = normalized[3]
                elif normalized[0] == 'от':
                    elem = normalized[2]
                    currency_index = 0
                    for character in elem:
                            is_letter = character.isalpha()
                            if is_letter:
                                break
                            currency_index += 1
                    min = int(elem[:currency_index])
                    max = None
                    currency = elem[currency_index:]
                elif normalized[0] == 'до':
                    elem = normalized[2]
                    currency_index = 0
                    for character in elem:
                        is_letter = character.isalpha()
                        if is_letter:
                            break
                        currency_index += 1
                    min = None
                    max = int(elem[:currency_index])
                    currency = elem[currency_index:]

            else:
                min = max = currency = None

        return min, max, currency

