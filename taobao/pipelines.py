# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import logging
from taobao.config import MONGO_URI, MONGO_DB
from scrapy.exceptions import DropItem


class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['id'])
            return item


class MongoPipeline(object):
    collection_name = 'test-1'

    def open_spider(self, spider):
        logging.info('TEST MESSAGE')
        self.client = pymongo.MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        try:
            self.db[self.collection_name].insert_one(dict(item))
        except Exception:
            pass
        return item
