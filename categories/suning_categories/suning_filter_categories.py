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
import os
import glob

from os import walk

import requests

from lxml import html
from urllib.parse import urljoin
from time import sleep

class loader(object):
    def get_file(self):
        with open('D:\\new_suning_category_results\\100\\0-20361-0.json') as f:
            urls = json.load(f)
        urls = urls[:1000]
        with open('suning_detail_test.json', 'w', encoding='utf8') as f:
            json.dump(urls, f, ensure_ascii=False, indent=4)

    def sort_detail_urls(self):
        out_path = 'D:\\dangdang\\dangdang_detail_urls_text'
        in_path = 'D:\\dangdang\\dangdang_detail_urls'

        for r, dirs, f in os.walk(in_path):
            for d in dirs:
                try:
                    for rr, dd, ff in os.walk(in_path + '\\' + d):
                        for json_f in ff:
                            json_file = in_path + '\\' + d + '\\' + json_f
                            with open(json_file) as f:
                                urls = json.load(f)
                                sort_urls = []
                                for url in urls:
                                    try:
                                        if url.get('url') and url.get('url') != '':
                                            sort_urls.append(url['url'] + '\n')
                                    except Exception as e:
                                        print(e, url)
                            sort_urls = list(set(sort_urls))
                            if not os.path.isdir(out_path + "\\" + d):
                                os.mkdir(out_path + '\\' + d)
                            path = out_path + '\\' + d + '\\' + json_f.replace('.json', '.txt')
                            with open(path, 'w') as f:
                                f.writelines(sort_urls)
                except Exception as e:
                    print(e)
                    continue

    # Check the results
    def check_results(self):
        in_path = 'D:\\Work\\day_results\\finished'
        today_in_path = 'D:\\Work\\day_results\\finished\\today'

        results = []
        finished_total = 0
        origin_total = 23700000

        for path, dirs, files in os.walk(in_path):
            for dir in dirs:
                d = os.path.join(path, dir)
                for p, _, sub_files in os.walk(d):
                    l = 0
                    for f in sub_files:
                        filename = os.path.join(p, f)
                        with open(filename, 'r') as fp:
                            urls = fp.readlines()
                        length = len(urls)
                        l += length
                finished_total += l
                results.append({dir: l})
        rate = (finished_total / origin_total) * 100
        current_resuls = {'results': results, 'rate': rate, 'total': finished_total}
        with open('D:\\Work\\day_results\\results.json', 'w', encoding='utf8') as f:
            json.dump(current_resuls, f, ensure_ascii=False, indent=4)

    # Get Count of Product URLs
    def get_count_urls(self):
        sort_urls = []
        # out_path = 'D:\\Suning\\final_suning_category_results_text'
        in_path = 'D:\Suning\\final_suning_category_text_update'
        results = []
        finished_total = 0

        for path, dirs, files in os.walk(in_path):
            for dir in dirs:
                d = os.path.join(path, dir)
                for p, _, sub_files in os.walk(d):
                    l = 0
                    for f in sub_files:
                        filename = os.path.join(p, f)
                        with open(filename, 'r') as fp:
                            urls = fp.readlines()
                        length = len(urls)
                        l += length
                finished_total += l
                results.append({dir: l})
        current_resuls = {'results': results, 'total': finished_total}
        with open('D:\dangdang\dangdang_total_results.json', 'w', encoding='utf8') as f:
            json.dump(current_resuls, f, ensure_ascii=False, indent=4)

    # Divide the product urls by 20KB
    def devide_capacity_url(self):
        in_path = 'D:\\dangdang\\dangdang_detail_urls_text'
        out_put_path = 'D:\\dangdang\\dangdang_detail_divide'

        for path, dirs, files in os.walk(in_path):
            for dir in dirs:
                d = os.path.join(path, dir)
                if not os.path.isdir(out_put_path + "\\" + dir):
                    os.mkdir(out_put_path + "\\" + dir)
                for p, _, sub_files in os.walk(d):
                    for f in sub_files:
                        divide_count = None
                        filename = os.path.join(p, f)
                        size = os.stat(filename).st_size / 1024
                        size = int(round(size, 0))
                        if size > 20:
                            divide_count = size / 20
                            divide_count = int(round(divide_count, 0))
                            divide_count += 1
                        with open(filename, 'r') as fp:
                            urls = fp.readlines()
                        f = f.replace('.txt', '')
                        if not os.path.isdir(out_put_path + "\\" + dir + "\\" + f):
                            os.mkdir(out_put_path + "\\" + dir + "\\" + f)
                        if divide_count:
                            divide_len = len(urls) / divide_count
                            divide_len = int(round(divide_len, 0))
                            for i in range(0, divide_count + 1):
                                k = i + 1
                                i = i * divide_len
                                j = i + divide_len
                                sub_urls = urls[i:j]
                                o_path = os.path.join(out_put_path, dir, f)
                                last_file_path = str(k) + '.txt'
                                if sub_urls:
                                    o_txt_path = os.path.join(o_path, last_file_path)
                                    with open(o_txt_path, 'w') as fp:
                                        fp.writelines(sub_urls)
                        else:
                            o_path = os.path.join(out_put_path, dir, f)
                            last_file_path = '1.txt'
                            o_txt_path = os.path.join(o_path, last_file_path)
                            with open(o_txt_path, 'w') as fp:
                                fp.writelines(urls)

    # Make Directory
    def make_dir(self):
        out_put_path = 'D:\\Suning\\suning_finished'
        for i in range(1, 42):
            j = i * 100
            os.mkdir(out_put_path + "\\" + str(j))
        return

def main(event, context):
    os = loader()
    # os.get_file()
    # os.sort_detail_urls()
    # os.get_sort_urls()
    os.check_results()
    # os.get_count_urls()
    # os.devide_capacity_url()
    # os.make_dir()

if __name__ == "__main__":
    main(0, 0)