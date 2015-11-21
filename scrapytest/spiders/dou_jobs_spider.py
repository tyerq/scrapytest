# -*- coding: utf-8 -*-

import scrapy

from scrapytest.items import JobItem

__author__ = 'tyerq'


class DouJobsSpider(scrapy.Spider):
    name = "dou_jobs"
    allowed_domains = ["dou.ua"]
    start_urls = [
        "http://jobs.dou.ua/"
    ]

    def parse(self, response):
        """
        main parse method
        :return: all categories with vacancies for each one
        """

        for sel in response.css("ul.cats > li.cat"):
            href = sel.xpath('a/@href').extract_first()
            name = sel.xpath('a/text()').extract_first()
            total = sel.xpath('em/text()').extract_first()
            url = response.urljoin(href)

            req = scrapy.Request(url=url, callback=self.parse_category)
            req.meta['category'] = name
            yield req

        others = response.css("div.b-recent-searches_also")
        hrefs = others.xpath('.//a/@href').extract()
        names = others.xpath('.//a/text()').extract()
        totals = others.xpath('.//em/text()').extract()
        urls = [response.urljoin(href) for href in hrefs]
        for url, name in zip(urls, names):
            req = scrapy.Request(url=url, callback=self.parse_category)
            req.meta['category'] = name
            yield req

    def parse_category(self, response):
        """
        get all jobs from a category
        :param response: Scrapy Response object
        :return: Scrapy Item objects with available info
        """
        hrefs = response.css("li.l-vacancy > div > div > a::attr('href')").extract()

        for href in hrefs:
            url = response.urljoin(href)
            req = scrapy.Request(url=url, callback=self.parse_job)
            req.meta['category'] = response.meta['category']
            yield req

    def parse_job(self, response):
        """
        get available info from users profile:
         - name
         - company
         - location
         - salary
        :param response: Scrapy Response object
        :return: Scrapy Item objects with available info
        """
        item = JobItem()

        item['name'] = response.css("h1.g-h2::text").extract_first()
        item['company'] = response.css("div.l-n > a:nth-child(1)::text").extract_first()
        item['location'] = response.css("span.place::text").extract_first().strip()
        item['salary'] = response.css("span.salary::text").extract_first()
        item['created'] = response.css("div.date::text").extract_first().strip()
        item['category'] = response.meta['category']

        yield item
