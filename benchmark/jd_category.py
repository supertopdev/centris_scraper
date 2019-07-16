from .batch_crawl import benchmark_print

category_links = [
    'https://list.jd.com/list.html?cat=9987,6880,6881',
    'https://list.jd.com/list.html?cat=9987,6880,12428',
    'https://list.jd.com/list.html?cat=9192,12190,12602',
    'https://list.jd.com/list.html?cat=9192,12190,12603',
    'https://list.jd.com/list.html?cat=9192,12190,12604',
    'https://list.jd.com/list.html?cat=9192,12190,12604',
    'https://list.jd.com/list.html?cat=9192,12190,12605',
    'https://list.jd.com/list.html?cat=1319,1524,1537',

    # Please change following links to another
    'https://list.jd.com/list.html?cat=9987,6880,6881',
    'https://list.jd.com/list.html?cat=9987,6880,12428',
    'https://list.jd.com/list.html?cat=9192,12190,12602',
    'https://list.jd.com/list.html?cat=9192,12190,12603',
    'https://list.jd.com/list.html?cat=9192,12190,12604',
    'https://list.jd.com/list.html?cat=9192,12190,12604',
    'https://list.jd.com/list.html?cat=9192,12190,12605',
    'https://list.jd.com/list.html?cat=1319,1524,1537',
    'https://list.jd.com/list.html?cat=9987,6880,6881',
    'https://list.jd.com/list.html?cat=9987,6880,12428',
    'https://list.jd.com/list.html?cat=9192,12190,12602',
    'https://list.jd.com/list.html?cat=9192,12190,12603',
    'https://list.jd.com/list.html?cat=9192,12190,12604',
    'https://list.jd.com/list.html?cat=9192,12190,12604',
    'https://list.jd.com/list.html?cat=9192,12190,12605',
    'https://list.jd.com/list.html?cat=1319,1524,1537',
    'https://list.jd.com/list.html?cat=9987,6880,6881',
    'https://list.jd.com/list.html?cat=9987,6880,12428',
    'https://list.jd.com/list.html?cat=9192,12190,12602',
    'https://list.jd.com/list.html?cat=9192,12190,12603',
    'https://list.jd.com/list.html?cat=9192,12190,12604',
    'https://list.jd.com/list.html?cat=9192,12190,12604',
    'https://list.jd.com/list.html?cat=9192,12190,12605',
    'https://list.jd.com/list.html?cat=1319,1524,1537',
]

spider_name = 'jd_product_link'
class_name = 'JdShelfPagesSpider'

def benchmark(max_parallel_jobs, output_path):
    benchmark_print(category_links, spider_name, class_name, max_parallel_jobs, output_path)
