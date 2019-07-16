import argparse
import subprocess
import os
import time
import json

MAIN_DIRECTORY = os.path.dirname(__file__)

def analysis(filename, spider_name='',log_file='scrapy.log', out_file='', image_path=''):
    time_map = {}

    if not os.path.isdir(image_path):
        os.mkdir(image_path)

    # for i in range(2, 100):
    i = 8
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
        'CONCURRENT_REQUESTS={}'.format(i),
        '-s',
        'CONCURRENT_REQUESTS_PER_DOMAIN={}'.format(i),
        '-s',
        'IMAGES_STORE={}'.format(image_path)
    ])
    end_time = time.time()
    diff_time = end_time - start_time
    time_map['p_{}'.format(i)] = diff_time
    print(i, diff_time)
    time.sleep(10)
    with open('result.json', 'w') as f:
        json.dump(time_map, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--read-file', default='result.json')
    parser.add_argument("-s", "--spider-name", help="spider name")
    parser.add_argument('-l', '--log-file')
    parser.add_argument('-o', '--out-file')
    parser.add_argument('-i', '--image-path')
    args = parser.parse_args()
    analysis(args.read_file, args.spider_name, args.log_file, args.out_file, args.image_path)

