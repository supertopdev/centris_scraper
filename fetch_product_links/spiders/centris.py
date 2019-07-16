# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

import re
import json
import requests
import traceback

from time import sleep
from lxml import html
from scrapy import Request, FormRequest
from urllib.parse import urljoin, urlencode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


from fetch_product_links.spiders import BaseProduct, cond_set_value
from fetch_product_links.utils import get_first_element

class CentrisProductsSpider(BaseProduct):
    name = 'centris_products'
    allowed_domains = ['centris.ca']

    start_urls = ['https://www.centris.ca']
    product_api_url = 'https://www.centris.ca/Mvc/Property/GetInscriptions'
    product_url = 'https://www.centris.ca/fr/propriete-commerciale~a-louer~montreal-ile?view=List'
    start_posistion = 0
    single_api_url = 'https://www.centris.ca/Mvc/Property/GetInscriptions'

    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/75.0.3770.100 Safari/537.36'
    }

    search_url = 'https://www.centris.ca/fr/propriete-commerciale~a-vendre~{keyword}?view=Thumbnail'

    get_key_req_url = 'https://www.centris.ca/Property/PropertyWebService.asmx/GetAutoCompleteData'

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self._start_requests, dont_filter=True)

    def _start_requests(self, response):
        data = {'startPosition': self.start_posistion}
        with open('urls.txt') as f:
            urls = f.readlines()

        for url in urls[0:1]:
            self.headers['Referer'] = self._clean_text(url)
            yield Request(
                url=self.product_api_url,
                method='POST',
                body=json.dumps(data),
                headers=self.headers,
                dont_filter=True
            )

    def parse(self, response):
        try:
            json_data = json.loads(response.text)
            result = json_data.get('d', {}).get('Result', {})
            tree_html = html.fromstring(result.get('html'))
        except Exception as e:
            print(e)

        page_length = (result.get('count') // 20) + 1

        for i in range(1, page_length):
            data = {'startPosition': 20 * i}
            yield Request(
                url=self.product_api_url,
                method='POST',
                body=json.dumps(data),
                headers=self.headers,
                callback=self.parse
            )

        product_links = tree_html.xpath("//a[contains(@class, 'a-more-detail')]/@href")

        options = Options()
        options.headless = True
        driver = webdriver.Chrome('D:\\chromedriver.exe', chrome_options=options)



        for i, link in enumerate(product_links):
            url = urljoin(response.url, link)
            driver.get(url)
            product = self.parse_single_product(driver.page_source)
            yield product

    def parse_single_product(self, response):
        product = {}
        tree_html = html.fromstring(response)
        title = ''.join(html.fromstring(response).xpath("//h1[@itemprop='category']//span/text()"))
        price = ''.join(html.fromstring(response).xpath("//div[@class='price']//span/text()"))[2:]
        description = self._clean_text(''.join(html.fromstring(response).xpath("//div[@itemprop='description']/text()")))
        construction_year = ''.join(html.fromstring(response).xpath("//td[text()='Année de construction']/following-sibling::td[1]/span/text()"))
        geo_coordinates = ''.join(html.fromstring(response).xpath("//div[@itemprop='geo']//meta/@content"))
        lot_area = ''.join(html.fromstring(response).xpath("//td[text()='Superficie disponible']/following-sibling::td[1]/span/text()"))
        parking = ''.join(html.fromstring(response).xpath("//td[text()='Nombre d’unités']/following-sibling::td[1]/span/text()"))
        product['title'] = title
        product['price'] = price
        product['description'] = description
        product['construction_year'] = construction_year
        product['geo_coordinates'] = geo_coordinates
        product['lot_area'] = lot_area
        product['parking'] = parking
        yield product

    def _clean_text(self, text):
        text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ")
        text = re.sub("&nbsp;", " ", text).strip()

        return re.sub(r'\s+', ' ', text)