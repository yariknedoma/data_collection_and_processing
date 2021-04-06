# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class Lesson8ScrapyPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram

    def process_item(self, item, spider):

        if item['being_scraped'] == item['profile_owner']:
            # получаем название коллекции по типу randomuser1_followers/following
            collection = self.mongo_base[item['being_scraped']+'_followers']
            del item['being_scraped']

        elif item['being_scraped'] == item['follower']:
            collection = self.mongo_base[item['being_scraped'] + '_following']
            del item['being_scraped']

        collection.insert_one(item)
        return item
