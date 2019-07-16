import argparse
import subprocess
import os
import time

MAIN_DIRECTORY = os.path.dirname(__file__)

def analysis(filename, spider_name='',log_file='scrapy.log', out_file='', parallel_threads=5):
    start_time = time.time()
    subprocess.run([
        'scrapy',
        'crawl',
        spider_name,
        '-a',
        'input_file={}'.format(os.path.join(MAIN_DIRECTORY, filename)),
        '-o',
        out_file,
        '-s',
        'LOG_FILE={}'.format(log_file),
        '-s',
        'CONCURRENT_REQUESTS={}'.format(parallel_threads),
        '-s',
        'CONCURRENT_REQUESTS_PER_DOMAIN={}'.format(parallel_threads)
    ])
    end_time = time.time()
    diff_time = end_time - start_time
    print(parallel_threads, diff_time)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--read-file', default='result.json')
    parser.add_argument("-s", "--spider-name", help="spider name")
    parser.add_argument('-l', '--log-file')
    parser.add_argument('-o', '--out-file')
    parser.add_argument('-p', '--parallel-threads')
    args = parser.parse_args()
    analysis(args.read_file, args.spider_name, args.log_file, args.out_file, args.parallel_threads)

