from .batch_crawl import benchmark_print
import json
import csv

product_urls = []
with open('/home/ubuntu/Category_URLs/categories/taobao/taobao_1.csv', 'r') as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        product_urls.append(row[0])

spider_name = 'taobao'
class_name = 'TaobaoProductsSpider'

def benchmark(max_parallel_jobs, output_path):
    benchmark_print(product_urls, spider_name, class_name, max_parallel_jobs, output_path)
