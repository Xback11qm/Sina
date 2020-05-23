# -*- coding: utf-8 -*-
import os

import scrapy
from  ..items import *

class SinaSpider(scrapy.Spider):
    name = 'sina'
    allowed_domains = ['sina.com.cn']
    start_urls = ['http://news.sina.com.cn/guide/']

    def parse(self, response):
        """提取内容:大标题  大链接  小标题  小链接"""
        div_list = response.xpath('//div[@id="tab01"]/div')
        for div in div_list:
            # 因为大标题+大链接 不需要交给调度器 所以此处不先创建item对象
            parent_name = div.xpath('./h3/a/text()|./h3/span/text()').get()
            parent_url = div.xpath('./h3/a/@href').get()
            if not parent_url:
                parent_url = 'http'
            # 每个大分类 下有好多小分类
            li_list = div.xpath('./ul/li')
            for li in li_list:
                item = SinaItem()
                item['son_name'] = li.xpath('./a/text()').get()
                item['son_url'] = li.xpath('./a/@href').get()
                item['parent_name'] = parent_name
                item['parent_url'] = parent_url
                # directory: ./data/体育/NBA/
                item['directory'] = '/home/tarena/Newsdata/{}/{}/'.format(item['parent_name'],item['son_name'])
                if not os.path.exists(item['directory']):
                    os.makedirs(item['directory'])
                # 把小分类的请求 交给调度器入队列
                yield scrapy.Request(url=item['son_url'],meta={"meta_1":item},callback=self.parse_son_url)

    def parse_son_url(self,response):
        """提取内容:小分类的url地址"""
        meta_1 = response.meta['meta_1']
        news_url_list = response.xpath('//a/@href').extract()
        for news_url in news_url_list:
            #通过观察规律:新闻的URL
            if news_url.startswith(meta_1['parent_url']) and news_url.endswith('.shtml'):
                #此时，把news_url交给调度器入队列 所以创建item对象
                item = SinaItem()
                item['news_url'] = news_url
                item['directory'] = meta_1['directory']
                item['parent_name'] = meta_1['parent_name']
                item['parent_url'] = meta_1['parent_url']
                item['son_name'] = meta_1['son_name']
                item['son_url'] = meta_1['son_url']

                yield scrapy.Request(url=item['news_url'],meta={'item':item},callback=self.get_content)


    def get_content(self,response):
        """提取新闻标题  新闻内容"""
        item = response.meta['item']
        item['news_head'] = response.xpath('//h1[@class="main-title"]/text() | //h1[@id="main-title"]/text()').get()
        item['news_content'] = "\n".join(response.xpath('//div[@class="article"]/p/text()|//div[@class="content"]/p/text()').extract())

        yield item






