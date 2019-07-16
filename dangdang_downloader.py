from utils.products_downloader import run_product_downloader
import argparse
import sys
import os

# Update stdout encoding for non-unicode console window
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

sys.path.append(os.getcwd())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--parallel-jobs", help="parallel jobs", default=16)
    parser.add_argument("-s", "--scan-path", help="scan path")
    args = parser.parse_args()

    spider_name = 'dangdang'
    class_name = 'DangDangProductsSpider'

    run_product_downloader(args.scan_path, args.parallel_jobs, spider_name, class_name)
