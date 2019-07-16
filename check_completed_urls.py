# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

import json
import os

class loader(object):
    # Check the results
    def check_results(self):
        suning_path = 'C:\\Users\\Administrator\\Documents\\Tasks'
        dangdang_path = 'C:\\Users\\Administrator\\Documents\\Tasks_Dang'
        # suning_path = 'D:\Work\Tasks'
        # dangdang_path = 'D:\Work\Tasks_Dang'

        self.divide_by_site('suning', suning_path)
        self.divide_by_site('dangdang', dangdang_path)

    def divide_by_site(self, sitename, result_path):
        suning_total = 23178331
        dangdang_total = 14722181
        parent_dir = None
        l = 0
        files_count = 0
        for s_path, s_dirs, s_files in os.walk(result_path):
            if not parent_dir and s_dirs:
                parent_dir = s_dirs[0]
            for s_dir in s_dirs:
                d = os.path.join(s_path, s_dir)
                for child_path, child_dirs, child_files in os.walk(d):
                    for child_dir in child_dirs:
                        child_d = os.path.join(child_path, child_dir)
                        for last_path, last_dir, last_files in os.walk(child_d):
                            for f in last_files:
                                if f.endswith('.json'):
                                    files_count += 1
                                    text_file = f.replace('.json', '.txt')
                                    filename = os.path.join(last_path, text_file)
                                    with open(filename, 'r') as fp:
                                        urls = fp.readlines()
                                    length = len(urls)
                                    l += length

        if sitename == 'suning':
            sunning_rate = (l / suning_total) * 100
            if parent_dir is not None:
                print(parent_dir + ':' + 'today_suning_count:', l)
            else:
                print('today_suning_count:', l)
            print('suning_rate:', sunning_rate)
            print('suning_file_count:', files_count)

        if sitename == 'dangdang':
            dangdang_rate = (l / dangdang_total) * 100
            if parent_dir is not None:
                print(parent_dir + ':' + 'today_dangdang_count:', l)
            else:
                print('today_dangdang_count:', l)
            print('dangdang_rate:', dangdang_rate)
            print('dangdang_file_count:', files_count)

def main(event, context):
    os = loader()
    os.check_results()

if __name__ == "__main__":
    main(0, 0)