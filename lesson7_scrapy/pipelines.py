# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import scrapy
import hashlib
from scrapy.utils.python import to_bytes


class Lesson7ScrapyPipeline:

    def process_item(self, item, spider):
        details_dict = dict()
        len_names = len(item['details_names'])
        len_definitions = len(item['details_definitions'])
        if len_names == len_definitions:
            for i in range(len_names):
                details_dict[item['details_names'][i]] = item['details_definitions'][i]
            del item['details_names']
            del item['details_definitions']
        item['details'] = details_dict

        return item


class PhotoScrapyPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None, *, item):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        folder = item['name']
        return f'full/{folder}/{image_guid}.jpg'

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item
