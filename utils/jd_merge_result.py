import json
import os
import sys
import time
from bisect import bisect_left
sys.path.append(os.getcwd())

def sorted_list_contains(values, x):
    i = bisect_left(values, x)
    return i != len(values) and values[i] == x

def combine_text_files(source_files, output_path):
    # Ignore pre combined files
    if os.path.exists(output_path):
        return

    links = []
    try:
        for filename in source_files:
            if not os.path.exists(filename):
                continue
            with open(filename, 'r', encoding='utf8') as f:
                new_links = []
                for line in f.readlines():
                    line = line.strip()
                    if not line or sorted_list_contains(links, line) or line in new_links:
                        continue
                    else:
                        new_links.append(line)

                links.extend(new_links)
                links.sort()
    except Exception as e:
        print(e)
        return

    with open(output_path, 'w', encoding='utf8') as f:
        for link in links:
            f.write(link + '\n')

    print("Output:", output_path)

def combine_json_files(source_files, output_path):
    # Ignore pre combined files
    if os.path.exists(output_path):
        return

    products = {}
    try:
        # Read all products
        for filename in source_files:
            if not os.path.exists(filename):
                continue

            with open(filename, 'r', encoding='utf8') as f:
                for new_product in json.load(f):
                    sku = new_product['sku_id']
                    if sku in products:
                        # Update fields only for duplicated products
                        current_product = products[sku]
                        for field in new_product:
                            if not field in current_product or not current_product[field] and new_product[field]:
                                current_product[field] = new_product[field]
                        continue
                    else:
                        products[sku] = new_product

        # Save products
        with open(output_path, 'w', encoding='utf8') as f:
            f.write('[')

            keys = list(products.keys())
            keys.sort()
            for i in range(len(keys)):
                f.write('\n' if i == 0 else ',\n')
                json.dump(products[keys[i]], f, ensure_ascii=False, indent=4)

            f.write('\n]')

        print("Output:", output_path)

    except Exception as e:
        print(e)
        return

def combine_output(source_directories, output_directory):
    if not source_directories or len(source_directories) == 0:
        return

    input_directory = source_directories[0]
    for fname in os.listdir(input_directory):
        child_source_names = [os.path.join(root, fname) for root in source_directories]
        child_output_name = os.path.join(output_directory, fname)

        input_path = child_source_names[0]
        if os.path.isdir(input_path):
            if not os.path.exists(child_output_name):
                os.mkdir(child_output_name)
            combine_output(child_source_names, child_output_name)
        else:
            if input_path.endswith('.txt'):
                combine_text_files(child_source_names, child_output_name)
            elif input_path.endswith('.json'):
                combine_json_files(child_source_names, child_output_name)

    combine_output(source_directories[1:], output_directory)

def get_index_filename(data_file_path):
    if data_file_path.endswith('.json'):
        return data_file_path[0:-5] + "_index.txt"

def build_index(output_directory, ignore_existing=False):
    if not os.path.isdir(output_directory):
        return

    for fname in os.listdir(output_directory):
        child_name = os.path.join(output_directory, fname)

        if os.path.isdir(child_name):
            build_index(child_name, ignore_existing)
        elif child_name.endswith('.json'):
            index_name = get_index_filename(child_name)
            if ignore_existing and os.path.exists(index_name):
                continue

            sku_list = []
            with open(child_name, 'r', encoding='utf8') as f:
                for product in json.load(f):
                    try:
                        sku_id = int(product['sku_id'])
                        sku_list.append(sku_id)
                    except:
                        pass
                sku_list.sort()

            with open(index_name, 'w', encoding='utf8') as f:
                f.writelines([str(sku_id) + '\n' for sku_id in sku_list])
            print("Index built:", index_name)

if __name__ == '__main__':
    source_directories = ['Y:\\Tasks\\Result', 'Y:\\Finished']
    output_directory = '..\\JD\\Old_Result'

    # combine_output(source_directories, output_directory)
    # build_index(output_directory, True)