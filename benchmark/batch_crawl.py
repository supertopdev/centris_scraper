from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import multiprocessing as mp
import os
import json
import time

def crawl(urls, spider_class, concurrent_requests, output_path):
    settings = get_project_settings()
    settings['CONCURRENT_REQUESTS'] = concurrent_requests
    settings['CONCURRENT_REQUESTS_PER_DOMAIN'] = concurrent_requests * 2
    settings['LOG_ENABLED'] = False
    if output_path:
        settings['FEED_FORMAT'] = 'json'
        settings['FEED_URI'] = output_path

    process = CrawlerProcess(settings)
    process.crawl(spider_class, product_urls=urls, productlist_urls=urls)
    process.start()

    return None

def get_crawl_time(links, spider_name, class_name, parallel_jobs=1, output_path=None):
    # Load spider class
    mod = __import__('fetch_product_links.spiders.{}'.format(spider_name), fromlist=[class_name])
    spider_class = getattr(mod, class_name)

    # Check parameters
    if not links:
        return 0

    if parallel_jobs < 1:
        parallel_jobs = 1

    procs = []

    # Run process for each jobs
    start_time = time.time()

    if parallel_jobs > 1:
        link_count = len(links)
        for i in range(0, parallel_jobs):
            index_from = (i * link_count) // parallel_jobs
            index_to = ((i + 1) * link_count) // parallel_jobs

            urls = links[index_from:index_to]
            if not urls:
                continue

            process_output_path = '%s.%d' % (output_path, i+1) if output_path else None

            proc = mp.Process(target=crawl, args=(urls, spider_class, parallel_jobs, process_output_path))
            procs.append(proc)
            proc.start()

        # Wait for the other processes
        for proc in procs:
            proc.join()
    else:
        process_output_path = '%s.%d' % (output_path, 1) if output_path else None
        crawl(links, spider_class, parallel_jobs, process_output_path)

    end_time = time.time()

    if output_path:
        values = []
        for i in range(0, parallel_jobs):
            process_output_path = '%s.%d' % (output_path, i+1)
            if os.path.exists(process_output_path):
                if os.path.getsize(process_output_path) > 0:
                    with open(process_output_path, 'r', encoding='utf8') as f:
                        data = json.load(f)
                        values.extend(data)
                os.remove(process_output_path)

        # Sort values by url
        sorted_values = []
        for _, url in enumerate(links):
            for j, v in enumerate(values):
                if v['url'] == url:
                    sorted_values.append(v)
                    values.pop(j)
                    break
        if values:
            sorted_values.extend(values)

        with open(output_path, "w", encoding='utf8') as f:
            f.write(json.dumps(sorted_values, ensure_ascii=False, indent=4))

    return end_time - start_time

def benchmark_print(links, spider_name, class_name, max_parallel_jobs, output_path=None):
    if not links:
        return
    if max_parallel_jobs < 1:
        max_parallel_jobs = 1

    for i in range(0, max_parallel_jobs):
        parallel_jobs = i + 1

        # Attach job count into output filename
        p = output_path.rfind('.')
        p = 0 if p < 0 else p
        output_file_path = output_path[0:p] + ('-%d' % parallel_jobs) + output_path[p:]

        print(parallel_jobs, get_crawl_time(links, spider_name, class_name, parallel_jobs, output_file_path))
