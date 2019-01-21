#!/usr/bin/env python
#-*-coding:utf-8-*-
from urllib import parse as urlparse
#import urlparse
import re
import hashlib
import scrapy
from lib import log
import time

from caoliu.items import CaoliuItem

class CaoLiuSpider(scrapy.Spider):
    name = "caoliu"
    host = "http://t66y.com"

    def start_requests(self):
        print("start")
        #yield scrapy.Request('http://www.t66y.com/thread0806.php?fid=7&search=&page=1', callback=self.parse)
        yield scrapy.Request('http://t66y.com/thread0806.php?fid=22&search=&page=1', callback=self.parse)

    def parse(self, response):
        urls = response.xpath(u'//*[contains(@class, "tr3 t_one")]//h3//@href').extract()
        print("urls={}".format(urls))
        log.notice("urls={}".format(urls))
        for url in urls[:]:
            if 'htm_data' not in url:
                urls.remove(url)
                continue
            url = urlparse.urljoin(self.host, url)
            log.notice("url={}".format(url))
            yield scrapy.Request(url, callback=self.parse_post, errback=self.handle_failure, dont_filter=True)

        next_page = self.get_next_page(response)
        time.sleep(1)
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse, errback=self.handle_failure, dont_filter=True)

    def get_next_page(self, response):
        ret = response.xpath(u'//*[contains(text(), "下一頁")]/@href').extract()[0]
        next_page = urlparse.urljoin(self.host, ret)
        print("next_page={}".format(next_page))
        #return None

        max_page = self.settings.get('MAX_PAGE', 100)
        max_page = 100
        next_page_no = re.findall(r'page=(\d+)', ret)
        print(max_page, next_page_no, next_page)
        if next_page_no:
            next_page_no = int(next_page_no[0])
        else:
            next_page_no = 2

        if next_page_no < max_page:
            return next_page
        else:
            return None

    def handle_failure(self, failure):
        url = failure.request.url
        log.notice("fail url={}".format(url))
        return
        if 'page' in url:
            yield scrapy.Request(url, callback=self.parse, errback=self.handle_failure, dont_filter=True)
        else:
            yield scrapy.Request(url, callback=self.parse_post, errback=self.handle_failure, dont_filter=True)

    def parse_post(self, response):
        log.notice("get res")
        log.notice("resp={}".format(response))

        title = response.xpath(u'//*[@class="tr1 do_not_catch"]//h4/text()').extract()[0]
        log.notice("title={} url={} ".format(title, response.url))
        # content = response.xpath(u'(//div[@class="tpc_content do_not_catch"])[1]').extract()[0]
        # ptime = response.xpath(u'(//*[@class="tr1"])[1]//*[@class="tipad"]//text()').extract()
        # ptime = ''.join(ptime)
        # ptime = re.findall(r'(\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2})', ptime)
        # if ptime:
        #     ptime = ptime[0]
        #
        item = CaoliuItem()
        # item['title'] = title
        # item['cat'] = '7'
        # item['cat_name'] = u'技术讨论区'
        # item['url'] = response.url
        # item['url_md5'] = hashlib.md5(response.url).hexdigest()
        # item['publish_time'] = ptime
        # item['content'] = content
        # log.notice("item= title={} url={}".format(title, response.url))

        yield item
