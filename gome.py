import argparse
import subprocess
import os
from time import sleep

MAIN_DIRECTORY = os.path.dirname(__file__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--read-directory", help="target spider name")
    parser.add_argument("-p", "--parallel-jobs", help="parallel jobs")
    args = parser.parse_args()
    read_directory = os.path.join(MAIN_DIRECTORY, '../{}'.format(args.read_directory))
    output_path = os.path.join(MAIN_DIRECTORY, '../results_{}'.format(args.read_directory))
    images_path = os.path.join(MAIN_DIRECTORY, '../images_{}'.format(args.read_directory))

    if not os.path.isdir(images_path):
        os.mkdir(images_path)

    if os.path.isdir(read_directory):
        if not os.path.isdir(output_path):
            os.mkdir(output_path)
        for r, d, f in os.walk(read_directory):
            for file in f:
                if '.json' not in file:
                    continue

                output_file = os.path.join(output_path, 'result_{}'.format(file))
                subprocess.run([
                    'scrapy',
                    'crawl',
                    'gome_products',
                    '-a',
                    'input_file={}'.format(os.path.join(r, file)),
                    '-o',
                    output_file if os.name != 'nt' else 'file:///{}'.format(output_file),
                    '-s',
                    'LOG_FILE={}'.format(output_file.replace('.json', '.log')),
                    '-s',
                    'IMAGES_STORE={}'.format(images_path),
                    '-s',
                    'CONCURRENT_REQUESTS={}'.format(args.parallel_jobs),
                    '-s',
                    'CONCURRENT_REQUESTS_PER_DOMAIN={}'.format(args.parallel_jobs)
                ])

                finished_directory = os.path.join(r, '../finished')
                if not os.path.isdir(finished_directory):
                    os.mkdir(finished_directory)

                os.rename(os.path.join(r, file), os.path.join(finished_directory, file))

                sleep(30)

    else:
        print('Can not read directory: {}'.format(read_directory))