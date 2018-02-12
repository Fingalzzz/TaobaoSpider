# -*- coding: utf-8 -*-
import json
import re

import scrapy
from scrapy.utils.project import get_project_settings

from taobao.items import TaobaoItem


class PCListSpider(scrapy.Spider):
    name = 'pclist'
    allowed_domains = [
        'www.taobao.com',
        's.taobao.com',
        'hws.m.taobao.com'
    ]
    start_urls = []
    custom_settings = {
        # 'JOBDIR': 'crawls/pclist',
        # 'LOG_LEVEL': 'INFO',
        # 'LOG_FILE': 'crawls/pclist.log'
    }

    def __init__(self):
        # set a list of keywords and initialize the start_urls
        init_url = 'https://s.taobao.com/search?cat=16&ajax=true&q={}&data-key=uniq&data-value=imgo'
        settings = get_project_settings()
        keywords = settings.get('KEYWORDS')
        for kwd in keywords:
            self.start_urls.append(init_url.format(kwd))
            # self.logger.info(init_url.format(kwd))

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
            itemlist = res['mods']['itemlist']['data']['auctions']
            # create item and yeild
            for item in itemlist:
                product = TaobaoItem()
                product['name'] = item['raw_title']
                # product['sale'] = item['view_sales']
                product['comment'] = item['comment_count']
                product['_id'] = item['nid']
                product['cover_url'] = item['pic_url'][2:]
                request = scrapy.Request(
                    'http://hws.m.taobao.com/cache/wdetail/5.0/?id={}'.format(item['nid']),
                    callback=self.parse_sale,
                    errback=self.errback_http)
                request.meta['item'] = product
                yield request
        except Exception:
            self.logger.error(response.body)

        # set url for next page
        num = response.url.split('=')[-1]
        if num == 'imgo':
            new_url = response.url.split('uniq')[0] \
                      + 's&uniq=imgo&data-value=44&s=0'
        elif num != '4180':
            base_url = response.url.split('data-value')[0] \
                       + 'data-value={}&s={}'
            new_url = base_url.format(self.addi(num, 88), self.addi(num, 44))
        yield scrapy.Request(
            new_url, callback=self.parse,
            errback=self.errback_http)

    def parse_sale(self, response):
        product = response.meta['item']
        try:
            res = json.loads(response.body_as_unicode())
        except Exception:
            request = scrapy.Request(
                'http://hws.m.taobao.com/cache/wdetail/5.0/?id={}'.format(product['nid']),
                callback=self.parse_sale,
                errback=self.errback_http)
            request.meta['item'] = product
            return request
        data = res['data']['apiStack'][0]['value']
        product['sale'] = re.search('totalSoldQuantity.+?(\d+)', data).group(1)
        cur_id = response.url.split('=')[1]
        request = scrapy.Request(
            'http://hws.m.taobao.com/cache/mtop.wdetail.getItemDescx/4.1/?data=%7B%22item_num_id%22%3A%22{}%22%7D'.format(
                cur_id),
            callback=self.parse_pic,
            errback=self.errback_http)
        request.meta['item'] = product
        return request

    def parse_pic(self, response):
        product = response.meta['item']
        res = json.loads(response.body_as_unicode())
        piclist = res['data']['images']
        picurl = list()
        for pic in piclist:
            picurl.append(pic)
        product['image_urls'] = picurl
        return product

    def addi(self, s, n):
        return str(int(s) + n)
