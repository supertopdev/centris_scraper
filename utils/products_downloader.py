import os
import sys
import json
import time
from datetime import datetime
from multiprocessing import Process, Queue, Lock
from multiprocessing.sharedctypes import RawValue
import threading
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from bisect import bisect_left

class Counter(object):
    def __init__(self, value=0):
        # RawValue because we don't need it to create a Lock:
        self.val = RawValue('i', value)
        self.lock = Lock()

    def add(self, value):
        with self.lock:
            self.val.value += value

    def value(self):
        with self.lock:
            return self.val.value

def seconds_to_hms(t):
    t = float(t)
    h = int(t / 3600)
    t = t - h * 3600
    m = int(t / 60)
    s = int(t - m * 60)
    return "%02d:%02d:%02d" % (h, m, s)

def run_product_downloader(scan_path, parallel_jobs, spider_name, class_name):
    if not os.path.isdir(scan_path):
        print("{} is not valid path".format(scan_path))
        return

    try:
        parallel_jobs = int(parallel_jobs)
        if parallel_jobs < 1:
            parallel_jobs = 1
    except:
        parallel_jobs = 1

    # Load spider class
    mod = __import__('fetch_product_links.spiders.{}'.format(spider_name), fromlist=[class_name])
    spider_class = getattr(mod, class_name)

    file_list = Queue()
    total_size = 0

    print("Loading task list...")

    for path, _, files in os.walk(scan_path):
        for name in files:
            filename = os.path.join(path, name)
            if filename.endswith('.txt'):
                output_path = filename[0:-3] + "json"
                if os.path.exists(output_path):
                    continue

                file_list.put(filename)
                total_size += os.path.getsize(filename)

    downloaded_size_counter = Counter()

    print("Start downloading...")

    procs = []
    idle_processes = Queue()
    while True:
        if file_list.empty():
            break
        filename = file_list.get_nowait()

        if len(procs) >= parallel_jobs:
            idle_process_index = idle_processes.get()
            procs.pop(idle_process_index)

        process_id = len(procs)
        proc = Process(target=do_downloading_job, args=(filename, spider_class, downloaded_size_counter, total_size, process_id, idle_processes))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()

def do_downloading_job(filename, spider_class, downloaded_size_counter, total_size, process_id, finished_processes_queue):
    print("Downloading", filename)

    start_time = time.time()
    output_path = filename[0:-3] + "json"
    download_products(filename, output_path, spider_class)
    elapsed_time = time.time() - start_time

    downloaded_size_counter.add(os.path.getsize(filename))
    completed_percent = downloaded_size_counter.value() * 100.0 / total_size
    remained_percent = 100 - completed_percent

    remained_time = elapsed_time / completed_percent * remained_percent if completed_percent > 0 else None

    print("  Completed: %.2f%%" % completed_percent,
        "    Elapsed time:", seconds_to_hms(elapsed_time),
        "    Remained time:", seconds_to_hms(remained_time) if remained_time else "",
        "    Current time:", datetime.now())

    finished_processes_queue.put(process_id)

def get_temp_output_path(output_path, id=None):
    if id == None:
        return '%s.tmp' % (output_path)
    return '%s.%d.tmp' % (output_path, id)

def get_predownloaded_products(output_path):
    predownloaded_products = []

    for id in [None, 0]:
        filename = get_temp_output_path(output_path, id)
        if os.path.exists(filename):
            try:
                body = ''
                with open(filename, 'r', encoding='utf8') as f:
                    body = f.read()

                try:
                    predownloaded_products.extend(json.loads(body))
                except json.JSONDecodeError:
                    try:
                        body += '{}]'
                        predownloaded_products.extend(json.loads(body))
                        predownloaded_products.pop()
                    except:
                        pass
            except:
                pass


    # Save items
    filename = get_temp_output_path(output_path, 0)
    with open(filename, "w", encoding='utf8') as f:
        f.write(json.dumps(predownloaded_products, ensure_ascii=False, indent=4))

    return predownloaded_products

def sorted_list_contains(values, x):
    i = bisect_left(values, x)
    return i != len(values) and values[i] == x

def eliminate_predownloaded_products(product_links, predownloaded_products):
    if not predownloaded_products:
        return

    predownloaded_links = [item['url'] for item in predownloaded_products]
    predownloaded_links.sort()

    for i in range(len(product_links) - 1, -1, -1):
        if sorted_list_contains(predownloaded_links, product_links[i]):
            product_links.pop(i)

def download_products(source, output_path, spider_class):
    # Load url list
    try:
        product_links = []
        with open(source, 'r', encoding='utf8') as f:
            product_links = [s.strip() for s in f.readlines()]

        if not product_links:
            return
    except:
        return

    # Start parallel downloading
    values = get_predownloaded_products(output_path)
    if values:
        eliminate_predownloaded_products(product_links, values)

    process_output_path = get_temp_output_path(output_path)
    if os.path.exists(process_output_path):
        os.remove(process_output_path)

    crawl(product_links, spider_class, process_output_path)

    # Get individual crawl result, including predownloaded
    if os.path.exists(process_output_path) and os.path.getsize(process_output_path) > 0:
        with open(process_output_path, 'r', encoding='utf8') as f:
            data = json.load(f)
            values.extend(data)

    # Remove temp file
    for id in [None, 0]:
        process_output_path = get_temp_output_path(output_path, id)
        if os.path.exists(process_output_path):
            os.remove(process_output_path)

    # Save to file
    with open(output_path, "w", encoding='utf8') as f:
        f.write(json.dumps(values, ensure_ascii=False, indent=4))

def crawl(urls, spider_class, output_path):
    settings = get_project_settings()
    settings['CONCURRENT_REQUESTS'] = 4
    settings['CONCURRENT_REQUESTS_PER_DOMAIN'] = 8
    settings['LOG_ENABLED'] = False
    if output_path:
        settings['FEED_EXPORT_ENCODING'] = 'utf-8'
        settings['FEED_FORMAT'] = 'json'
        settings['FEED_URI'] = 'file:///{}'.format(output_path.replace('\\', '/')) if ':' in output_path else output_path

    process = CrawlerProcess(settings)
    process.crawl(spider_class, product_urls=urls, productlist_urls=urls)
    process.start()

    return None
