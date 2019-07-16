import argparse
import json
import os
import re
from bisect import bisect_left

# Update stdout encoding for non-unicode console window
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

def read_sku_list(path):
    # Read sku list from file
    sku_list = []

    try:
        with open(path, 'r') as f:
            for link in f.readlines():
                sku = re.search(r'jd.com/(\d+).htm', link)
                if sku:
                    sku_list.append(int(sku.group(1)))
    except:
        return None

    return sku_list

def write_sku_list(path, sku_list):
    with open(path, 'w') as f:
        for sku in sku_list:
            f.write("https://item.jd.com/%d.html\n" % sku)

def get_downloaded_sku_list(path):
    sku_list = []

    try:
        index_path = path[0:-5] + "_index.txt"
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf8') as f:
                sku_list = [int(sku_id.strip()) for sku_id in f.readlines()]
        else:
            with open(path, 'r', encoding='utf8') as f:
                products = json.load(f)
                if isinstance(products, list):
                    sku_list = [int(product['sku_id']) for product in products]
    except:
        pass

    return sku_list

def sorted_list_contains(values, x):
    i = bisect_left(values, x)
    return i != len(values) and values[i] == x

def subtract_sorted_list(a, b):
    c = []
    for v in a:
        if not sorted_list_contains(b, v):
            c.append(v)

    return c

def prepare_directory(path):
    if not os.path.isdir(path):
        if os.path.exists(path):
            return False
        os.makedirs(path)

    return True

SKU_LIST_FILENAME = 'downloaded.txt'

def load_sku_list():
    try:
        with open(SKU_LIST_FILENAME, 'r') as f:
            return [int(l.strip()) for l in f.readlines()]
    except:
        return None

def save_sku_list(sku_list):
    try:
        if sku_list and isinstance(sku_list, list):
            with open(SKU_LIST_FILENAME, 'w') as f:
                f.writelines([str(sku) + '\n' for sku in sku_list])
    except:
        pass

def normalize_ordered_list(sku_list):
    if not sku_list or not isinstance(sku_list, list):
        return

    sku_list.sort()
    l = len(sku_list)
    i = 1
    j = 1
    while j < l:
        if sku_list[j] != sku_list[j - 1] and i != j:
            sku_list[i] = sku_list[j]
            i += 1
        j += 1

    for _ in range(i, len(sku_list)):
        sku_list.pop()

def scan_tasks(task_root, downloaded_root, new_task_root):
    if not os.path.isdir(task_root) or not os.path.isdir(downloaded_root):
        return

    prepare_directory(new_task_root)

    # Get sku list of all downloaded products
    downloaded_sku_list = load_sku_list()
    if downloaded_sku_list is None:
        downloaded_sku_list = []
        for path, _, files in os.walk(downloaded_root):
            for name in files:
                filename = os.path.join(path, name)
                if not filename.endswith('.json'):
                    continue

                print("Reading downloaded file:", filename)
                downloaded_sku_list.extend(get_downloaded_sku_list(filename))

        normalize_ordered_list(downloaded_sku_list)
        save_sku_list(downloaded_sku_list)

    # Export missed links
    total_missed = 0
    saved_sku_list = []
    for path, _, files in os.walk(task_root):
        for name in files:
            filename = os.path.join(path, name)
            if not filename.endswith('.txt'):
                continue

            # Ignore empty files
            sku_list = read_sku_list(filename)
            if not sku_list:
                continue

            print("Checking task file:", filename)

            # Get missing product links
            sku_list.sort()
            missed_sku_list = subtract_sorted_list(sku_list, downloaded_sku_list)
            missed_sku_list = subtract_sorted_list(missed_sku_list, saved_sku_list)
            total_missed += len(missed_sku_list)

            if missed_sku_list:
                category_path = os.path.relpath(os.path.dirname(filename), task_root)
                task_path = os.path.join(new_task_root, category_path)
                prepare_directory(task_path)

                task_path = os.path.join(task_path, name)
                write_sku_list(task_path, missed_sku_list)

            saved_sku_list = sorted(saved_sku_list + missed_sku_list)

    return (len(downloaded_sku_list), total_missed)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--task-path", help="product link file path")
    parser.add_argument("-s", "--scan-path", help="downloaded result path")
    parser.add_argument("-d", "--dest_path", help="path to save remained task")
    args = parser.parse_args()

    downloaded_count, missed_count = scan_tasks(args.task_path, args.scan_path, args.dest_path)
    print("Total downloaded:", downloaded_count)
    print("Missed count:", missed_count)
