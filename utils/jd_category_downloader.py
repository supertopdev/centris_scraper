import json
import os
import sys
import re
import requests
import time
from queue import Queue
from threading import Thread
from lxml import html
from shutil import copyfile

sys.path.append(os.getcwd())

def get_page_content(link):
    for _ in range(10):
        try:
            r = requests.get(link)
            if r.status_code == 200 and r.url == link:
                return r.content
            # else:
            #     print("Invalid response:", link, r.status_code)
        except:
            pass

        time.sleep(.5)

    return

def crawl_categories(link, output_path):
    product_links = []
    cur_page = 1
    total_pages = None
    total_count = 0

    while True:
        page_link = "{category_link}&page={page_num}&sort=sort_dredisprice_asc&trans=1&JL=6_0_0".format(category_link=link, page_num=cur_page)
        page_content = get_page_content(page_link)
        tree = html.fromstring(page_content)

        if not total_pages:
            elem = tree.xpath('//span[@class="fp-text"]/i')
            if elem:
                total_pages = int(elem[0].text)
        if not total_count:
            elem = tree.xpath('//div[@class="st-ext"]/span')
            if elem:
                total_count = int(elem[0].text)

        links = tree.xpath("//li//div[@class='p-img']//a/@href")
        if not links:
            links = tree.xpath("//ul[@class='search-list']//li[contains(@class, 'search-item')]/a[1]/@href")
        product_links.extend(links)

        cur_page += 1
        if not total_pages or cur_page > total_pages:
            break
        else:
            time.sleep(.2)

    if len(product_links) < total_count:
        print("The category %s contains %d products, but got %d items only" % (link, total_count, len(product_links)))
    else:
        with open(output_path, 'w', encoding='utf8') as f:
            for link in product_links:
                f.write(('https:' if link.startswith('//') else '') + link + '\n')

        print(os.path.abspath(output_path))

    return

def threaded_download_product_links(tasks):
    try:
        while True:
            task = tasks.get_nowait()
            if not task:
                return

            # Don't download existing file
            output_path = task['name']
            if os.path.exists(output_path):
                continue

            # Start crawling
            crawl_categories(task['link'], output_path)
    except:
        pass

class JdCategoryDownloader(object):
    CATEGORY_REQ_LINK = 'https://dc.3.cn/category/get?&callback=getCategoryCallback'
    CATEGORY_LIST_URL = 'https://list.jd.com/list.html?cat='

    JD_CATEGORY_DATA_FILE = 'jd_categories.json'
    JD_CATEGORIES_RESULT = 'jd_categories_result.json'
    JD_NEW_CATEGORY_DATA_FILE = 'jd_new_categories.json'

    ALWAYS_UPDATE_CATEGORIES = False
    DOWNLOAD_JOBS = 16

    def __init__(self):
        self.tasks = Queue()
        return

    def extract_product_links(self, root):
        if not self.set_output_directory(root):
            return

        new_categories = self.get_categories_from_file("final_jd_urls.json")
        # old_categories = self.get_categories()
        # self.update_categories(new_categories, old_categories)
        # self.save_new_categories(new_categories)
        # total_count = self.calc_total_products(new_categories)
        # print("Total Count:", total_count)
        # self.save_new_categories(new_categories)
        self.add_task(new_categories, 'Categories')

        # Download product links by category
        self.do_download()

        # # Remove duplicated items
        # self.remove_duplicated('Categories')

        return

    def set_output_directory(self, root):
        if not os.path.exists(root):
            os.mkdir(root)

        if os.path.isdir(root):
            os.chdir(root)
            return True

        print("Please input valid directory name")

    def get_categories(self):
        categories = []

        if not self.ALWAYS_UPDATE_CATEGORIES and os.path.exists(self.JD_CATEGORIES_RESULT):
            try:
                with open(self.JD_CATEGORIES_RESULT, 'r', encoding='utf8') as f:
                    return json.load(f)
            except:
                pass

        # Retrieve or open categories data
        # if True or os.path.exists(self.JD_CATEGORY_DATA_FILE):
        category_contents = requests.get(self.CATEGORY_REQ_LINK).text
        category_contents = category_contents[20:-1] # Remove "getCategoryContents(", ")"
        category_data = json.loads(category_contents)['data']

        with open(self.JD_CATEGORY_DATA_FILE, 'w', encoding='utf8') as f:
            f.write(category_contents)
        # else:
        #     with open(self.JD_CATEGORY_DATA_FILE, 'r', encoding='utf8') as f:
        #         category_contents = json.load(f)
        #         category_data = category_contents['data']

        # Build category tree
        for c0 in category_data:
            e = { 'link': None, 'name': None, 'children': [] }
            for subitem in c0['s']:
                e['children'].append(self.parse_subitem_node(subitem))
            # for channel in c0['t']:
            #     e['children'].append(self.parse_channel_node(channel))

            e['name'] = '/'.join(child['name'] for child in e['children'])
            categories.append(e)

        with open(self.JD_CATEGORIES_RESULT, 'w', encoding='utf8') as f:
            json.dump(categories, f, ensure_ascii=False, indent=4)

        return categories

    def get_categories_from_file(self, filename):
        new_categories = []

        if not self.ALWAYS_UPDATE_CATEGORIES and os.path.exists(self.JD_NEW_CATEGORY_DATA_FILE):
            try:
                with open(self.JD_NEW_CATEGORY_DATA_FILE, 'r', encoding='utf8') as f:
                    return json.load(f)
            except:
                pass

        def find_category_element(categories, names):
            if not names:
                return

            i = -1
            for k in range(len(categories)):
                if categories[k]['name'] == names[0]:
                    i = k
                    break
            if i < 0:
                i = len(categories)
                categories.append({
                    "name": names[0],
                    "children": []
                })

            if len(names) == 1:
                return categories[i]
            else:
                return find_category_element(categories[i]['children'], names[1:])

        def add_new_category(new_categories, link):
            page_content = get_page_content(link)
            tree = html.fromstring(page_content)

            category_names = []

            # Use simple method to extract titles
            title = tree.xpath('//title')
            if not title:
                print("Invalid category link:", link)
                return

            title = title[0].text.strip().replace('、', '/')
            p = title.find('【')
            if p >= 0:
                title = title[0:p]

            category_names = title.split(' ')
            if len(category_names) == 3:
                category_names.remove('')
                category_names.reverse()
            else:
                category_names = []
                category_elements = tree.xpath('//div[@class="crumbs-nav-item one-level"]/a')
                if category_elements:
                    category_names.append(category_elements[0].text)

                category_elements = tree.xpath('//div[@class="menu-drop"]/div[@class="trigger"]/span[@class="curr"]')
                for elem in category_elements:
                    category_names.append(elem.text)

            new_category = find_category_element(new_categories, category_names)
            new_category['link'] = link

            return

        with open(filename, 'r', encoding='utf8') as f:
            for link in json.load(f):
                add_new_category(new_categories, link)

        self.save_new_categories(new_categories)

        return new_categories

    def calc_total_products(self, category):
        # Calculate total count by sum of children
        children = category['children'] if 'children' in category else category
        if children:
            total_count = sum(self.calc_total_products(child) for child in children)
            if isinstance(category, list):
                return total_count
            elif not 'count' in category:
                category['count'] = total_count
            return total_count

        # Get count of products in current category link
        if 'link' in category and category['link']:
            if not 'count' in category:
                total_count = self.get_product_count_in_category(category['link'])
                if total_count is not None:
                    category['count'] = total_count
                print(category['link'])

        return category.get('count', 0)

    def get_product_count_in_category(self, category_link):
        page_content = get_page_content(category_link)
        tree = html.fromstring(page_content)
        elem = tree.xpath('//div[@class="st-ext"]/span')
        if elem:
            return int(elem[0].text)
        else:
            elem = tree.xpath('//div[@class="s-title"]/em') # for list.jd.hk
            if elem:
                return int(elem[0].text)
        print("Cannot get product count from link:", category_link)

    def save_new_categories(self, new_categories):
        with open(self.JD_NEW_CATEGORY_DATA_FILE, 'w', encoding='utf8') as f:
            json.dump(new_categories, f, ensure_ascii=False, indent=4)

    def update_categories(self, new_categories, old_categories):
        def find_in_old_categories(categories, link):
            if 'link' in categories:
                if categories['link'] == link:
                    return [categories['name']]

            old_children = categories['children'] if 'children' in categories else categories
            for child in old_children:
                names = find_in_old_categories(child, link)
                if names:
                    new_names = [categories['name']] if 'name' in categories else []
                    new_names.extend(names)
                    return new_names

        children = new_categories['children'] if 'children' in new_categories else new_categories
        for category in children:
            link = category.get('link', None)
            if link:
                names = find_in_old_categories(old_categories, link)
                if names:
                    names[0] = names[0].replace('/', '+')
                    category['old'] = '/'.join(names)
            if category['children']:
                self.update_categories(category['children'], old_categories)

        return

    def parse_subitem_node(self, node):
        if not node:
            return None

        e = {}
        e['link'], e['name'], _, _ = self.extract_properties(node['n'])
        e['children'] = []
        for child in node['s']:
            e['children'].append(self.parse_subitem_node(child))

        return e

    def parse_channel_node(self, node):
        e = {}
        e['link'], e['name'], _, _ = self.extract_properties(node)
        e['children'] = []

        return e

    def extract_properties(self, category_token):
        link, name, image_url, _ = category_token.split('|')
        if re.match(r'(\d+)\-(\d+)(\-(\d+))?$', link):
            link = self.CATEGORY_LIST_URL + link.replace('-', ',')

        return link, name, image_url, None

    def add_task(self, elem, root=''):
        # root level
        if isinstance(elem, list):
            for child in elem:
                self.add_task(child, root)
            return

        output_path = os.path.join(root, elem['name'].replace('/', '+'))
        if elem['children']:
            if not os.path.exists(output_path):
                os.mkdir(output_path)

            for child in elem['children']:
                self.add_task(child, output_path)
            return

        output_path += '.txt'
        if os.path.exists(output_path):
            return

        if 'link' in elem:
            self.tasks.put({
                'link': elem['link'],
                'name': output_path
            })

    def do_download(self):
        self.downloaders = []
        if self.DOWNLOAD_JOBS == 1:
            threaded_download_product_links(self.tasks)
        else:
            for _ in range(self.DOWNLOAD_JOBS):
                downloader = Thread(target=threaded_download_product_links, args=(self.tasks,))
                self.downloaders.append(downloader)
                downloader.start()

            for downloader in self.downloaders:
                downloader.join()

    def remove_duplicated(self, path=None):
        sub_categories = []
        link_files = []
        for c in os.listdir(path):
            child_path = os.path.join(path, c) if path else c
            if os.path.isdir(child_path):
                sub_categories.append(child_path)
            elif child_path.endswith('.txt'):
                link_files.append(child_path)

        # Get all links in sub category
        children_sku_list = []
        for fname in sub_categories:
            children_sku_list.extend(self.remove_duplicated(fname))

        # Get all links in text files:
        sku_list = []
        for fname in link_files:
            sku_list2 = self.read_sku_from_file(fname)
            if sku_list2:
                sku_list = sorted(sku_list + sku_list2)

        # Remove duplicated links by children
        # In that case, the directory has only 1 text file and sub categories
        if (sku_list and len(link_files) == 1) and self.sorted_list_has_same(sku_list, children_sku_list):
            sku_list = self.subtract_sorted_list(sku_list, children_sku_list)
            self.write_sku_list(link_files[0], sku_list)

        sku_list = sorted(sku_list + children_sku_list)
        if sku_list:
            print(path, len(sku_list))

        return sku_list

    def read_sku_from_file(self, path):
        # Read sku list from file
        sku_list = []
        with open(path, 'r') as f:
            for link in f.readlines():
                sku = re.search(r'jd.com/(\d+).htm', link)
                if sku:
                    sku_list.append(int(sku[1]))

        sku_list.sort()

        # Remove duplicated items
        duplicated_count = 0
        for i in range(len(sku_list) - 1, 0, -1):
            if sku_list[i] == sku_list[i - 1]:
                duplicated_count += 1
                sku_list.pop(i)

        # Save updated result
        if duplicated_count > 0:
            self.write_sku_list(path, sku_list)

        return sku_list

    def write_sku_list(self, path, sku_list):
        with open(path, 'w') as f:
            for sku in sku_list:
                f.write("https://item.jd.com/%d.html\n" % sku)

        print(path, "updated!")
        return

    def subtract_sorted_list(self, a, b):
        len1 = len(a)
        len2 = len(b)
        c = []
        i = j = 0
        while i < len1 and j < len2:
            if a[i] < b[j]:
                c.append(a[i])
                i += 1
            elif b[j] < a[i]:
                j += 1
            else:
                i +=1
                j +=1

        c.extend(a[i:])
        return c

    def sorted_list_has_same(self, a, b):
        len1 = len(a)
        len2 = len(b)
        i = j = 0
        while i < len1 and j < len2:
            if a[i] < b[j]:
                i += 1
            elif b[j] < a[i]:
                j += 1
            else:
                return True

        return False

if __name__ == '__main__':
    spider = JdCategoryDownloader()
    spider.extract_product_links('../JD')
