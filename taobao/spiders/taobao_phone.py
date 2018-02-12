# -*- coding: utf-8 -*-
import json

import scrapy


class PhoneListSpider(scrapy.Spider):
    name = 'phonelist'
    allowed_domains = [
        's.m.taobao.com'
    ]
    start_urls = []
    custom_settings = {
        # 'JOBDIR': 'crawls/phonelist-1',
        # 'LOG_LEVEL': 'INFO'
    }

    def __init__(self):
        # set a list of keywords and initialize the start_urls
        init_url = 'https://s.m.taobao.com/search?q={}&m=api4h5&cat=16&style=list&n=44&page='
        keywords = self.settings.get('KEYWORDS')
        for kwd in keywords:
            self.start_urls.append(init_url.format(kwd))

    def start_requests(self):
        for u in self.start_urls:
            yield scrapy.Request(
                u, callback=self.parse,
                errback=self.errback_http)

    def errback_http(self, failure):
        self.logger.error(repr(failure))

    def parse(self, response):
        res = json.loads(response.body_as_unicode())
        try:
            items = res['listItem']
            # create item and yeild
            for item in items:
                yield {
                    'name': item['name'],
                    'sale': item['sold'],
                    'comment': item['commentCount'],
                    '_id': item['item_id'],
                    'cover_url': item['img2'][2:]
                }
        except Exception:
            self.logger.error(response.body)
        # set url for next page

        url_blk = response.url.split('=')
        if url_blk[-1] is '':
            url_blk[-1] = '0'
        else:
            url_blk[-1] = str(int(url_blk) + 1)
        # maximum page is 100
        self.logger.info('CURRENT PAGE IS {}'.format(url_blk[-1]))
        if url_blk[-1] != 101:
            yield scrapy.Request(
                '='.join(url_blk), callback=self.parse,
                errback=self.errback_http)
