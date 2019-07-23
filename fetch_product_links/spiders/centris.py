# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

import re
import json

from sys import platform
from lxml import html
from scrapy import Request
from urllib.parse import urljoin
from selenium import webdriver
from translate import Translator

from fetch_product_links.spiders import BaseProduct


class CentrisProductsSpider(BaseProduct):
    name = 'centris_products'
    allowed_domains = ['centris.ca']
    start_urls = [
        'https://www.centris.ca/en/properties~for-rent?view=Thumbnail',
        'https://www.centris.ca/en/commercial-properties~for-rent?view=Thumbnail',
        'https://www.centris.ca/en/commercial-properties~for-sale?view=Thumbnail',
        'https://www.centris.ca/en/properties~for-sale?view=Thumbnail'
    ]
    product_api_url = 'https://www.centris.ca/Mvc/Property/GetInscriptions'

    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/75.0.3770.100 Safari/537.36'
    }

    search_url = 'https://www.centris.ca/fr/propriete-commerciale~a-vendre~{keyword}?view=Thumbnail'
    get_key_req_url = 'https://www.centris.ca/Property/PropertyWebService.asmx/GetAutoCompleteData'

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url=self._clean_text(url),
                meta={'start_position': 0, 'url': url},
                callback=self._start_requests,
                dont_filter=True
            )

    def _start_requests(self, response):
        start_position = response.meta.get('start_position')
        url = response.meta.get('url')
        data = {'startPosition': start_position}

        response.meta['start_position'] = start_position
        self.headers['Referer'] = self._clean_text(url)
        yield Request(
            url=self.product_api_url,
            method='POST',
            body=json.dumps(data),
            headers=self.headers,
            dont_filter=True,
            meta=response.meta
        )

    def parse(self, response):
        url = response.meta.get('url')
        if response.meta.get('start_position') > 19:
            start_position = response.meta.get('start_position')

            data = {'startPosition': start_position}

            yield Request(
                url=self.product_api_url,
                method='POST',
                body=json.dumps(data),
                headers=self.headers,
                dont_filter=True,
                meta=response.meta,
                callback=self._get_product_
            )
        else:
            start_position = response.meta.get('start_position')
            try:
                json_data = json.loads(response.text)
                result = json_data.get('d', {}).get('Result', {})
                tree_html = html.fromstring(result.get('html'))
            except Exception as e:
                result = None
                print(e)

            product_links = tree_html.xpath("//a[contains(@class, 'a-more-detail')]/@href")

            for i, link in enumerate(product_links):
                url = urljoin(response.url, link)

                yield Request(url, callback=self.parse_single_product)

            for start_position in range(result.get('count')):
                start_position = 1 + start_position

                data = {'startPosition': start_position}

                yield Request(
                    url=self.product_api_url,
                    method='POST',
                    body=json.dumps(data),
                    headers=self.headers,
                    dont_filter=True,
                    meta=response.meta,
                    callback=self._get_product_
                )



    def parse_single_product(self, response):
        product = {}

        products = response.xpath("//div[@class='grid_3']//div[@class='description']//table//tr")
        title = ' '.join(response.xpath("//h1[@itemprop='category']//span/text()").extract())
        address = ' '.join(response.xpath("//h2[@itemprop='address']/text()").extract())
        price = ' '.join(response.xpath("//div[@class='price']//span/text()").extract())
        description = self._clean_text(' '.join(response.xpath("//div[@itemprop='description']/text()").extract()))
        bathbeds = ' '.join(response.xpath("//div[@class='teaser']//span/text()").extract())
        walkscore = ' '.join(response.xpath("//div[@class='walkscore']//span/text()").extract())
        geo_coordinates = ' '.join(response.xpath("//div[@itemprop='geo']//meta/@content").extract())

        product['title'] = title
        product['address'] = address
        product['price'] = price
        product['description'] = description
        product['bedbaths'] = bathbeds
        product['walkscore'] = walkscore
        product['geo_coordinates'] = geo_coordinates

        for item in products:

            key = self._clean_text(item.xpath('.//td/text()').extract_first())
            value = self._clean_text(item.xpath('.//td/span/text()').extract_first())

            product[key] = value

        return product

    def _clean_text(self, text):
        text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ")
        text = re.sub("&nbsp;", " ", text).strip()
        return re.sub(r'\s+', ' ', text)
    def _get_product_(self, response):
        product = {}
        start_position = response.meta.get('start_position')
        try:
            json_data = json.loads(response.text)
            result = json_data.get('d', {}).get('Result', {})
            tree_html = html.fromstring(result.get('html'))
        except Exception as e:
            result = None
            print(e)
        products = tree_html.xpath("//div[@class='grid_3']//div[@class='description']//table//tr")
        title = ' '.join(tree_html.xpath("//h1[@itemprop='category']//span/text()"))
        address = ' '.join(tree_html.xpath("//h2[@itemprop='address']/text()"))
        price = ' '.join(tree_html.xpath("//div[@class='price']//span/text()"))
        description = self._clean_text(' '.join(tree_html.xpath("//div[@itemprop='description']/text()")))
        bathbeds = ' '.join(tree_html.xpath("//div[@class='teaser']//span/text()"))
        walkscore = ' '.join(tree_html.xpath("//div[@class='walkscore']//span/text()"))
        geo_coordinates = ' '.join(tree_html.xpath("//div[@itemprop='geo']//meta/@content"))

        product['title'] = title
        product['address'] = address
        product['price'] = price
        product['description'] = description
        product['bedbaths'] = bathbeds
        product['walkscore'] = walkscore
        product['geo_coordinates'] = geo_coordinates

        for item in products:
            key = self._clean_text(item.xpath('.//td/text()')[0])
            value = self._clean_text(item.xpath('.//td/span/text()')[0])

            product[key] = value

        return product