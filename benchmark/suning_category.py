from .batch_crawl import benchmark_print
import json
# category_links = [
#     'https://list.suning.com/0-503031-0.html',
#     'https://list.suning.com/0-502547-0.html',
#     'https://list.suning.com/0-340590-0.html',
#     'https://list.suning.com/0-502710-0.html'
# ]
with open('/home/ubuntu/categories/suning/suning_500.json', encoding='utf8') as f:
    category_links = json.load(f)

spider_name = 'suning_product_link'
class_name = 'SuningShelfPagesSpider'

def benchmark(max_parallel_jobs, output_path):
    benchmark_print(category_links, spider_name, class_name, max_parallel_jobs, output_path)
