# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

import json
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

import csv
import re
import json
import requests

from lxml import html
from urllib.parse import urljoin
from time import sleep

class loader(object):

    def get_file(self):
        suning_url = "https://www.suning.com/"
        categories = []
        try:
            self.driver = webdriver.PhantomJS(executable_path='/home/ubuntu/phantomjs/bin/phantomjs',
                                              service_log_path='/home/ubuntu/phantomjs/ghostdriver.log')
            self.driver.get(suning_url)
            parent_cat_elems = self.driver.find_elements_by_xpath('//ul[@class="index-list"]//li')
            for elem in parent_cat_elems:
                e = {'link': None, 'name': None, 'children': []}
                names = []
                category1 = []
                href_tag = elem.find_elements_by_xpath(".//a")
                for t in href_tag:
                    name = t.get_attribute('text')
                    url = t.get_attribute('href')
                    category1.append(url)
                category2_urls, category3_urls = self.get_sub_cate(category1, elem)
                categories.append({'category1': category1, 'category2': category2_urls, 'category3': category3_urls})

        except Exception as e:
            sleep(5)
            print(e)
        category_2_urls = []
        category_1_urls = []
        category_3_urls = []
        for c in categories:
            category1 = c.get('category1')
            category2 = c.get('category2')
            category3 = c.get('category3')
            for c1 in category1:
                category_1_urls.append(c1)
            for c2 in category2:
                category_2_urls.append(c2)
            for c3 in category3:
                category_3_urls.append(c3)

        category_1_urls = list(set(category_1_urls))
        category_2_urls = list(set(category_2_urls))
        category_3_urls = list(set(category_3_urls))

        with open('selenium_category_1.json', 'w', encoding='utf8') as f:
            json.dump(category_1_urls, f, ensure_ascii=False, indent=4)

        with open('selenium_category_2.json', 'w', encoding='utf8') as f:
            json.dump(category_2_urls, f, ensure_ascii=False, indent=4)

        with open('selenium_category_3.json', 'w', encoding='utf8') as f:
            json.dump(category_3_urls, f, ensure_ascii=False, indent=4)

    def categories_with_names(self):
        suning_url = "https://www.suning.com/"
        categories = []
        try:
            self.driver = webdriver.PhantomJS(executable_path='/home/ubuntu/phantomjs/bin/phantomjs',
                                              service_log_path='/home/ubuntu/phantomjs/ghostdriver.log')
            self.driver.get(suning_url)
            parent_cat_elems = self.driver.find_elements_by_xpath('//ul[@class="index-list"]//li')
            for elem in parent_cat_elems:
                e = {'link': None, 'name': None, 'children': []}
                names = []
                category1 = []
                href_tag = elem.find_elements_by_xpath(".//a")
                for t in href_tag:
                    name = t.get_attribute('text')
                    url = t.get_attribute('href')
                    names.append(name)
                    category = {'name': name, 'link': url, 'children': []}
                    e['children'].append(category)
                e['name'] = '/'.join(names)
                category = self.get_sub_cate(e, elem)
                categories.append(category)


        except Exception as e:
            sleep(5)
            print(e)

        with open('full_selenium_categories.json', 'w', encoding='utf8') as f:
            json.dump(categories, f, ensure_ascii=False, indent=4)


    def get_sub_cate(self, e, elem):
        while True:
            try:
                hover = ActionChains(self.driver).move_to_element(elem)
                hover.perform()
                break
            except Exception as e:
                print(e)
                sleep(5)
                continue

        while True:
            try:
                dl_cat_links = self.driver.find_elements_by_xpath('//div[@class="cate-list"]//dl')
                for i, dl_link in enumerate(dl_cat_links):
                    dt_tag = dl_link.find_elements_by_xpath(".//dt//a")[0]
                    dt_tag_name = dt_tag.get_attribute('text')
                    dt_tag_url = dt_tag.get_attribute('href')
                    category2 = {'name': dt_tag_name, 'link': dt_tag_url, 'children': []}
                    e['children'][0]['children'].append(category2)

                    dd_tag = dl_link.find_elements_by_xpath(".//dd//a")
                    category_3 = []
                    for d in dd_tag:
                        name = d.get_attribute('text')
                        url = d.get_attribute('href')
                        category3 = {'name': name, 'url': url, 'children': []}
                        e['children'][0]['children'][i]['children'].append(category3)
                return e

            except Exception as e:
                sleep(5)
                continue

    def get_categories_from_api(self):
        suning_site_url = "https://www.suning.com/"
        suning_categories_url = "https://list.suning.com/"

        site_html = requests.get(suning_site_url).text

        category_site_html = html.fromstring(requests.get(suning_categories_url).text)
        category_urls = category_site_html.xpath(
            "//div[contains(@class, 'title-box')]//div[contains(@class, 't-right')]//a/@href")

        category_urls = list(set(category_urls))
        category_update_urls = []
        for url in category_urls:
            if url and url.startswith('//'):
                url = 'https:' + url
            category_update_urls.append(url)
        category_update_urls = list(set(category_update_urls))

        with open('categories_from_api.json', 'w', encoding='utf8') as f:
            json.dump(category_update_urls, f, ensure_ascii=False, indent=4)

    def sum_selenium_categories(self):
        with open('selenium_category_1.json') as f:
            selenium1 = json.load(f)
        with open('selenium_category_2.json') as f:
            selenium2 = json.load(f)
        sum_categories = selenium1 + selenium2
        sum_categories = list(set(sum_categories))

        with open('sum_selenium.json', 'w', encoding='utf8') as f:
            json.dump(sum_categories, f, ensure_ascii=False, indent=4)

    def list_suning_categories(self):
        list_suning_urls = []
        search_suning_urls = []
        shop_suning_urls = []

        with open('selenium_category_3.json') as f:
            selenium3 = json.load(f)

        with open('sum_selenium.json') as f:
            sum_selenium = json.load(f)
        url_format = 'https://list.suning.com/'
        for url in selenium3:
            if 'list.suning.com/' in url:
                if re.findall(r'suning.com/(\d+)\-(\d+)\-(\d+)\-(\d+)', url):
                    digits = re.findall(r'\d+', url)[:3]
                    digits = '-'.join(digits)
                    url = url_format + digits + '.html'
                list_suning_urls.append(url)
            elif 'search.suning.com/' in url:
                search_suning_urls.append(url)
            else:
                shop_suning_urls.append(url)

        for url in sum_selenium:
            if 'list.suning.com/' in url:
                if re.findall(r'suning.com/(\d+)\-(\d+)\-(\d+)\-(\d+)', url):
                    digits = re.findall(r'\d+', url)[:3]
                    digits = '-'.join(digits)
                    url = url_format + digits + '.html'
                list_suning_urls.append(url)
            elif 'search.suning.com/' in url:
                search_suning_urls.append(url)
            else:
                shop_suning_urls.append(url)

        list_suning_urls = list(set(list_suning_urls))
        search_suning_urls = list(set(search_suning_urls))
        shop_suning_urls = list(set(shop_suning_urls))

        with open('list_suning.json', 'w', encoding='utf8') as f:
            json.dump(list_suning_urls, f, ensure_ascii=False, indent=4)

        with open('search_suning.json', 'w', encoding='utf8') as f:
            json.dump(search_suning_urls, f, ensure_ascii=False, indent=4)

        with open('shop_suning.json', 'w', encoding='utf8') as f:
            json.dump(shop_suning_urls, f, ensure_ascii=False, indent=4)

    def get_sort_api(self):
        url = 'https://lib.suning.com/api/jsonp/cb/sortList_v6-threeSortLoad.jsonp'
        return url

def main(event, context):
    os = loader()
    # os.get_file()
    os.categories_with_names()
    # os.get_categories_from_api()
    # os.sum_selenium_categories()
    # os.list_suning_categories()
    # os.get_sort_api()


if __name__ == "__main__":
    main(0, 0)