import json
import requests
from lxml import html

class loader(object):
    def get_file(self):
        url = "https://www.allrecipes.com/recipes/"
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                resp_content = resp.text
                tree_html = html.fromstring(resp_content)
                cat_links = tree_html.xpath("//div[@class='all-categories-col']//section//ul//li//a/@href")
                cat_links = cat_links[:-1]
                with open('reciep_category.json', 'w', encoding='utf8') as f:
                    json.dump(cat_links, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(e)

def main(event, context):
    lo = loader()
    lo.get_file()
if __name__ == "__main__":
    main(0, 0)