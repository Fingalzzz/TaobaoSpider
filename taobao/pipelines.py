# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import logging

import pymongo
import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline


class CustomImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        # for url in
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url, meta=item)

    def file_path(self, request, response=None, info=None):
        image_guid = hashlib.sha1(request.url.encode('utf-8')).hexdigest()
        folder = request.meta['_id']
        return '%s/%s.jpg' % (folder, image_guid)


class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['_id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['_id'])
            return item


class MongoPipeline(object):
    collection_name = 'scrapy_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        try:
            self.db[self.collection_name].insert_one(dict(item))
        except Exception:
            logging.ERROR('FAILED insert into MongoDB')
        return item
