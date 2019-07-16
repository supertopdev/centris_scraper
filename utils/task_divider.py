import argparse
import os
import sys
import shutil

def divide_download_list(scan_path, divide_count):
    total_size = 0
    filelist = []

    # Get all file list
    for path, _, files in os.walk(scan_path):
        for name in files:
            filename = os.path.join(path, name)
            if filename.endswith('.txt'):
                filesize = os.path.getsize(filename)
                if filesize == 0:
                    continue

                filelist.append(filename)
                total_size += filesize

    # Divide into subdirectories
    divide_size = (total_size + divide_count - 1) // divide_count

    for i in range(divide_count):
        task_size = 0
        while filelist and task_size < divide_size:
            filename = filelist.pop()
            destname = os.path.join(scan_path, "Task_%02d" % (i + 1), filename[len(scan_path) + 1:])
            destroot = os.path.dirname(destname)

            if not os.path.isdir(destroot):
                os.makedirs(destroot)

            shutil.copyfile(filename, destname)
            task_size += os.path.getsize(destname)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--divide-count", help="divide count", default=40)
    parser.add_argument("-s", "--scan-path", help="scan path")
    args = parser.parse_args()

    divide_count = int(args.divide_count)
    if divide_count > 1:
        divide_download_list(args.scan_path, divide_count)