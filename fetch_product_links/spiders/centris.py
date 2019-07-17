# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

import re
import json

from lxml import html
from scrapy import Request
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fetch_product_links.spiders import BaseProduct

class CentrisProductsSpider(BaseProduct):
    name = 'centris_products'
    allowed_domains = ['centris.ca']

    with open('urls.txt') as f:
        urls = f.readlines()
    start_urls = ['https://www.centris.ca']
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
        for url in self.urls:
            if url and url.split('/')[-1].isdigit():
                yield Request(
                    url=self._clean_text(url),
                    meta={'url': url},
                    dont_filter=True
                )
            else:
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
        if url and url.split('/')[-1].isdigit():
            product = self.get_data_from_selenium(url)
            yield product
        else:
            start_position = response.meta.get('start_position')
            try:
                json_data = json.loads(response.text)
                result = json_data.get('d', {}).get('Result', {})
                tree_html = html.fromstring(result.get('html'))
            except Exception as e:
                print(e)

            page_length = result.get('count') // 20
            if start_position > page_length * 20:
                return

            product_links = tree_html.xpath("//a[contains(@class, 'a-more-detail')]/@href")

            for i, link in enumerate(product_links):
                url = urljoin(response.url, link)
                product = self.get_data_from_selenium(url)
                yield product

            start_position = 20 + start_position
            response.meta['start_position'] = start_position
            yield Request(
                url=self.start_urls[0],
                meta=response.meta,
                callback=self._start_requests,
                dont_filter=True
            )

    def parse_single_product(self, response, url):
        product = {}
        tree_html = html.fromstring(response)
        title = ''.join(tree_html.xpath("//h1[@itemprop='category']//span/text()"))
        price = ''.join(tree_html.xpath("//div[@class='price']//span/text()"))
        description = self._clean_text(''.join(tree_html.xpath("//div[@itemprop='description']/text()")))
        construction_year = ''.join(tree_html.xpath("//td[text()='Année de construction']/following-sibling::td[1]/span/text()"))
        geo_coordinates = ''.join(tree_html.xpath("//div[@itemprop='geo']//meta/@content"))
        lot_area = ''.join(tree_html.xpath("//td[text()='Superficie disponible']/following-sibling::td[1]/span/text()"))
        parking = ''.join(tree_html.xpath("//td[text()='Nombre d’unités']/following-sibling::td[1]/span/text()"))
        bathbeds = ''.join(tree_html.xpath("//div[@class='teaser']//span/text()"))
        building_style = ''.join(tree_html.xpath("//td[text()='Building style']/following-sibling::td[1]/span/text()"))
        add_features = ''.join(tree_html.xpath("//td[text()='Additional features']/following-sibling::td[1]/span/text()"))
        pool = ''.join(tree_html.xpath("//td[text()='Swimming pool']/following-sibling::td[1]/span/text()"))

        product['url'] = url
        product['title'] = title
        product['price'] = price
        product['description'] = description
        product['construction_year'] = construction_year
        product['geo_coordinates'] = geo_coordinates
        product['lot_area'] = lot_area
        product['parking'] = parking
        product['bedbaths'] = bathbeds
        product['building_style'] = building_style
        product['add_features'] = add_features
        product['pool'] = pool
        return product

    def get_data_from_selenium(self, url):
        # options = Options()
        # options.headless = True
        driver = webdriver.PhantomJS(executable_path='phantomjs/bin/phantomjs.exe')
        # driver = webdriver.Chrome('D:\\chromedriver.exe', chrome_options=options)
        driver.get(url)
        resp = driver.page_source
        driver.quit()

        product = self.parse_single_product(resp, url)
        return product

    def _clean_text(self, text):
        text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ")
        text = re.sub("&nbsp;", " ", text).strip()
        return re.sub(r'\s+', ' ', text)