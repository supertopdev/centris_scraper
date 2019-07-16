import argparse

import sys
import os
sys.path.append(os.getcwd())

from products_downloader import run_product_downloader

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--parallel-jobs", help="parallel jobs", default=16)
    parser.add_argument("-s", "--scan-path", help="scan path")
    args = parser.parse_args()

    spider_name = 'jd'
    class_name = 'JdProductsSpider'

    run_product_downloader(args.scan_path, args.parallel_jobs, spider_name, class_name)
