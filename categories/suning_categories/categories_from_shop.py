# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

import json
from time import sleep
# from selenium import webdriver
# from selenium.webdriver.common.action_chains import ActionChains
from fetch_product_links.utils import get_first_element
import csv
import zipfile
import re
import json
import requests
import os
import shutil

from lxml import html
from urllib.parse import urljoin
from time import sleep

class loader(object):

    def get_file(self):
        suning_lists = []
        search_lists = []
        other_lists = []
        item_lists = []

        is_urls = []
        non_urls = []

        with open('shop_suning.json') as f:
            shop_categories = json.load(f)
        shop_categories = list(set(shop_categories))
        for url in shop_categories:
            try:
                if not 'product.suning.com/' in url:
                    resp = requests.get(url).text
                    tree_html = html.fromstring(resp)
                    links = tree_html.xpath(".//a/@href")
                    links = list(set(links))
                    for link in links:
                        suning_lists, search_lists, other_lists, item_lists = self.save_suning_list(link, suning_lists, search_lists, other_lists, item_lists)

                    if suning_lists:
                        is_urls.append(url)
                    else:
                        non_urls.append(url)
                else:
                    item_lists.append(url)
            except Exception as e:
                print(url + ':', e)
                continue

        suning_lists = list(set(suning_lists))
        search_lists = list(set(search_lists))
        other_lists = list(set(other_lists))
        item_lists = list(set(item_lists))
        with open('shop_suning_list.json', 'w', encoding='utf8') as f:
            json.dump(suning_lists, f, ensure_ascii=False, indent=4)
        with open('shop_search_urls.json', 'w', encoding='utf8') as f:
            json.dump(search_lists, f, ensure_ascii=False, indent=4)
        with open('shop_other_urls.json', 'w', encoding='utf8') as f:
            json.dump(other_lists, f, ensure_ascii=False, indent=4)
        with open('shop_item_urls.json', 'w', encoding='utf8') as f:
            json.dump(item_lists, f, ensure_ascii=False, indent=4)

    def save_suning_list(self, link, suning_lists, search_lists, other_lists, item_lists):
        if link:
            if link.startswith('//'):
                link = 'https:' + link
            if 'list.suning.com/' in link:
                suning_lists.append(link)
            elif 'search.suning.com/' in link:
                search_lists.append(link)
            elif 'product.suning.com/' in link:
                item_lists.append(link)
            else:
                other_lists.append(link)

        return suning_lists, search_lists, other_lists, item_lists

    def filter_suning_list(self):
        try:
            with open('shop_suning_list.json', encoding='utf8') as f:
                shop_categories = json.load(f)
        except Exception as e:
            print(e)
        url_format = 'https://list.suning.com/'
        urls = []
        for url in shop_categories:
            if re.findall(r'suning.com/(\d+)', url):
                if re.findall(r'suning.com/(\d+)\-(\d+)\-(\d+)\-(\d+)', url):
                    digits = re.findall(r'\d+', url)[:3]
                    digits = '-'.join(digits)
                    url = url_format + digits + '.html'
                if '?keyword=' in url:
                    url = re.search('(.*?)\?keyword', url)
                    url = url.group(1) if url else url
                urls.append(url)
        urls = list(set(urls))
        with open('shop_update_urls.json', 'w', encoding='utf8') as f:
            json.dump(urls, f, ensure_ascii=False, indent=4)

    def sum_suning_urls(self):
        with open('shop_update_urls.json', encoding='utf8') as f:
            shop_update_categories = json.load(f)

        with open('categories_from_api.json', encoding='utf8') as f:
            categories_api = json.load(f)

        with open('list_suning.json', encoding='utf8') as f:
            list_suning_categories = json.load(f)

        lists =  shop_update_categories + categories_api + list_suning_categories
        lists = list(set(lists))

        with open('final_urls.json', 'w', encoding='utf8') as f:
            json.dump(lists, f, ensure_ascii=False, indent=4)

    def sum_search_urls(self):
        with open('search_suning.json', encoding='utf8') as f:
            search_suning = json.load(f)

        with open('shop_search_urls.json', encoding='utf8') as f:
            shop_search_urls = json.load(f)

        lists = search_suning + shop_search_urls
        lists = list(set(lists))

        with open('final_search_urls.json', 'w', encoding='utf8') as f:
            json.dump(lists, f, ensure_ascii=False, indent=4)

    def final_urls(self):
        with open('final_urls.json', encoding='utf8') as f:
            final_urls = json.load(f)

        final_urls = list(set(final_urls))
        with open('final_update_urls.json', 'w', encoding='utf8') as f:
            json.dump(final_urls, f, ensure_ascii=False, indent=4)

    def classifcation_urls(self):
        with open('final_urls.json', encoding='utf8') as f:
            category_urls = json.load(f)
        default_dir = '/home/ubuntu/categories/suning/'
        try:
            for i in range(90):
                i = i * 100
                j = i + 100
                dir = 'suning_' + str(j) + '.json'
                dir = default_dir + dir
                urls = category_urls[i:j]
                with open(dir, 'w', encoding='utf8') as f:
                    json.dump(urls, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(e, j)


    def suning_get_title_from_category(self):
        category_link_temp = 'https://list.suning.com/%s.html'
        out_put = 'E:\suning\suning_detail_devide_3000_4100_titles'
        suning_path = 'E:\suning\suning_detail_devide_3000_4100'
        for s_path, s_dirs, s_files in os.walk(suning_path):
            for s_dir in s_dirs:
                d = os.path.join(s_path, s_dir)
                for child_path, child_dirs, child_files in os.walk(d):
                    for c_dir in child_dirs:

                        url = category_link_temp % c_dir
                        resp = requests.get(url).text
                        tree_html = html.fromstring(resp)
                        first_catogory_title = get_first_element(tree_html.xpath("//div[@id='search-path']//a[@class='result-right']/@title"))
                        temp_path = os.path.join(out_put, self._clean_text(first_catogory_title))
                        if not os.path.isdir(temp_path):
                            os.mkdir(temp_path)

                        second_category_titles = tree_html.xpath("//div[@id='search-path']//dl//dt//a[@sa-data and @title]/@title")

                        try:
                            for title in second_category_titles:
                                temp_path = os.path.join(temp_path, self._clean_text(title))
                                if not os.path.isdir(temp_path):
                                    os.mkdir(temp_path)
                            for p, d, f in os.walk(os.path.join(child_path, c_dir)):
                                for file in f:
                                    if '.txt' in file:
                                        shutil.copy(os.path.join(p, file), os.path.join(temp_path, '{}_{}'.format(c_dir, file)))
                        except Exception as e:
                            print(e)

    def dangdang_get_title_from_category(self):
        categories = []
        category_link_temp = 'http://category.dangdang.com/%s.html'
        e_link_temp = 'http://e.dangdang.com/%s.html'
        out_put = 'E:\\dangdang\\dangdang_json_title_from_category_id\\result.json'
        dangdang_path = 'E:\dangdang\dangdang_finished_json'
        for s_path, s_dirs, s_files in os.walk(dangdang_path):
            for s_dir in s_dirs:
                d = os.path.join(s_path, s_dir)
                for child_path, child_dirs, child_files in os.walk(d):
                    for c_dir in child_dirs:
                        category = {}
                        category[c_dir] = []
                        if 'list-' in c_dir:
                            url = e_link_temp % c_dir
                        else:
                            url = category_link_temp % c_dir
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                                 'Chrome/73.0.3683.86 Safari/537.36',
                                   'Upgrade-Insecure-Requests': '1',
                                   }
                        if 'e.dangdang.com' in url:
                            headers['Host'] = 'e.dangdang.com'
                        else:
                            headers['Host'] = 'category.dangdang.com'
                        # for i in range(3):
                        #     try:
                        #         resp = requests.get(url, headers=headers)
                        #         if resp.ok:
                        #             resp = resp.text
                        #             break
                        #     except Exception as e:
                        #         print(e)
                        try:
                            resp = requests.get(url, headers=headers).text
                            tree_html = html.fromstring(resp)
                            first_catogory_title = None
                            second_category_titles = []

                            if not 'e.dangdang.com' in url:
                                catogory_titles = tree_html.xpath("//div[@class='crumbs_fb_left']"
                                                                  "//a[@name='breadcrumb-category' and contains(@class, 'a')]/text()")
                                if catogory_titles:
                                    first_catogory_title = catogory_titles[0]
                                    second_category_titles = catogory_titles[1:]
                            else:
                                first_catogory_title = tree_html.xpath('//div[@id="bookClass"]/text()')
                                if first_catogory_title:
                                    first_catogory_title = first_catogory_title[0][0:2]

                                category_titles = tree_html.xpath("//div[contains(@class, 'selected')]//a//h3/text()")
                                if catogory_titles:
                                    second_category_titles = category_titles[0:]
                            if first_catogory_title:
                                category[c_dir].append(first_catogory_title)
                            if second_category_titles:
                                for title in second_category_titles:
                                    category[c_dir].append(title)
                            categories.append(category)
                        except Exception as e:
                            print(e)

        with open(out_put, 'w', encoding='utf8') as f:
            json.dump(categories, f, ensure_ascii=False, indent=4)

    def json_suning_get_title_from_category(self):
        categories = []
        category_link_temp = 'https://list.suning.com/%s.html'
        suning_path = 'E:\\suning\\final_suning_category_divide_update_'
        out_put = 'E:\\suning\\suning_json_title_from_category_id\\result.json'
        for s_path, s_dirs, s_files in os.walk(suning_path):
            for s_dir in s_dirs:
                d = os.path.join(s_path, s_dir)
                for child_path, child_dirs, child_files in os.walk(d):
                    for c_dir in child_dirs:
                        category = {}
                        category[c_dir] = []
                        url = category_link_temp % c_dir
                        resp = requests.get(url).text
                        tree_html = html.fromstring(resp)
                        first_catogory_title = get_first_element(tree_html.xpath("//div[@id='search-path']//a[@class='result-right']/@title"))
                        category[c_dir].append(first_catogory_title)
                        second_category_titles = tree_html.xpath("//div[@id='search-path']//dl//dt//a[@sa-data and @title]/@title")

                        try:
                            for title in second_category_titles:
                                category[c_dir].append(title)
                            categories.append(category)
                        except Exception as e:
                            print(e)
        with open(out_put, 'w', encoding='utf8') as f:
            json.dump(categories, f, ensure_ascii=False, indent=4)

    def remove_zip(self):
        dangdang_path = 'D:\dangdang\dangdang_detail_divide_test'
        for s_path, s_dirs, s_files in os.walk(dangdang_path):
            for s_dir in s_dirs:
                d = os.path.join(s_path, s_dir)
                for child_path, child_dirs, child_files in os.walk(d):
                    for c_dir in child_dirs:
                        if c_dir.endswith('.zip'):
                            os.remove(c_dir)

    @staticmethod
    def _clean_text(text):
        text = text.replace(',', '+').replace('/', '_').replace('\\', '_')
        return re.sub("[\n\t\r]", "", text).strip()
    @staticmethod
    def zipdir(path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))

    @staticmethod
    def remove_text_file():
        in_path = "E:\\Scraing_Work\\Alibaba 1688\\alibaba_links_finished"
        try:
            for s_path, s_dirs, s_files in os.walk(in_path):
                for s_dir in s_dirs:
                    d = os.path.join(s_path, s_dir)
                    for child_path, child_dirs, child_files in os.walk(d):
                        for c_dir in child_dirs:
                            child_d = os.path.join(child_path, c_dir)
                            for sub_child_path, sub_child_dirs, sub_child_files in os.walk(child_d):
                                for cat_file in sub_child_files:
                                    if cat_file.endswith('.log'):
                                        os.remove(os.path.join(sub_child_path, cat_file))
        except Exception as e:
            print(e)

    def remove_random_dir_text_file(self, in_path):

        try:
            for s_path, s_dirs, s_files in os.walk(in_path):
                if s_files:
                    for s_file in s_files:
                        if s_file.endswith('.log'):
                            os.remove(os.path.join(s_path, s_file))
                for s_dir in s_dirs:
                    d = os.path.join(s_path, s_dir)
                    self.remove_random_dir_text_file(d)

        except Exception as e:
            print(e)

    def remove_log(self, in_path):
        try:
            for s_path, s_dirs, s_files in os.walk(in_path):
                if s_files:
                    for s_file in s_files:
                        update_values = []
                        if s_file.endswith('.txt'):
                            text_path = os.path.join(s_path, s_file)
                            with open(text_path, 'r') as f:
                                values = f.readlines()
                                for v in values:
                                    v = v.split('html')[0] + 'html' + '\n'
                                    update_values.append(v)
                            os.remove(text_path)
                            with open(text_path, 'w') as f:
                                f.writelines(update_values)
                for s_dir in s_dirs:
                    d = os.path.join(s_path, s_dir)
                    self.remove_log(d)

        except Exception as e:
            print(e)

    def text_to_json(self):
        in_path = 'E:\Scraing_Work\yhd\Tasks'
        for s_path, s_dirs, s_files in os.walk(in_path):
            for s_file in s_files:
                text_path = os.path.join(s_path, s_file)
                # output_path = text_path.replace('.json', '.txt')
                with open(text_path, 'r') as f:
                    # values = f.read()
                    # values = json.loads(values)
                    values = f.readlines()
                urls = []
                os.remove(text_path)
                for v in values:
                    # url = v.get('url')
                    urls.append('https://item.yhd.com/{}.html'.format(v.replace('\n', '')) + '\n')
                with open(text_path, 'w') as f:
                    f.writelines(urls)

    def clear_json(self):
        in_path = 'E:\\Scraing_Work\\sports_teams\\basketball.json'
        out_path = 'E:\\Scraing_Work\\sports_teams\\basketball_new.json'
        with open(in_path, encoding='utf-8') as f:
            data = f.read()
        with open(out_path, 'w', encoding='utf8') as f:
            json.dump(json.loads(data), f, ensure_ascii=False, indent=4)

def main(event, context):
    lo = loader()
    #
    # os.filter_suning_list()os.get_file()
    # os.sum_suning_urls()
    # os.sum_search_urls()
    # os.final_urls()
    # os.classifcation_urls()
    # lo.suning_get_title_from_category()
    # lo.json_suning_get_title_from_category()
    # lo.dangdang_get_title_from_category()
    # lo.remove_text_file()
    # in_path = "E:\\Scraing_Work\\Alibaba 1688\\alibaba_links_finished\\filtered"
    # lo.remove_random_dir_text_file(in_path)
    # lo.remove_log(in_path)
    # lo.text_to_json()
    lo.clear_json()

if __name__ == "__main__":
    main(0, 0)