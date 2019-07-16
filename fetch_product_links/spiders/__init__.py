from scrapy import Spider, Request
import json
import re


class BaseProductLinksSpider(Spider):

    productlist_url = None
    productlist_urls = None
    num_pages = None

    HEADERS = {}

    def __init__(
            self,
            productlist_url=None,
            productlist_urls=None,
            start_idx=None,
            end_idx=None,
            read_file=None,
            output_directory=None,
            *args, **kwargs
    ):

        self.num_pages = int(kwargs.pop('num_pages', '9999'))

        self.productlist_url = productlist_url
        self.productlist_urls = productlist_urls if productlist_urls else []

        if self.productlist_url:
            self.productlist_urls.append(self.productlist_url)

        if read_file and start_idx and end_idx:
            start_idx = int(start_idx)
            end_idx = int(end_idx)
            with open(read_file, 'r') as f:
                data = json.load(f)
                f.close()

            end_idx = end_idx if len(data) >= end_idx else len(data)
            self.productlist_urls += [
                v
                for v in data[start_idx: end_idx]
                if v
            ]

        self.output_directory = output_directory

        super(BaseProductLinksSpider, self).__init__(*args, **kwargs)

    @staticmethod
    def get_cat_name(link):
        return None

    def start_requests(self):
        if self.productlist_urls:
            for link in self.productlist_urls:
                cat_name = self.get_cat_name(link)
                meta = {}
                if cat_name:
                    meta['cat_name'] = cat_name
                yield Request(url=link, headers=self.HEADERS, dont_filter=True, meta=meta)

    def _scrape_product_links(self, response):
        """_scrape_product_links(response:Response)
                :iter<tuple<str, SiteProductItem>>

        Returns the products in the current results page and a SiteProductItem
        which may be partially initialized.
        """
        raise NotImplementedError

    def _scrape_next_results_page_link(self, response):
        """_scrape_next_results_page_link(response:Response):str

        Scrapes the URL for the next results page.
        It should return None if no next page is available.
        """
        raise NotImplementedError

    def _scrape_total_matches(self, response):
        """_scrape_total_matches(response:Response):int

        Scrapes the total number of matches of the search term.
        """
        raise NotImplementedError

    def parse(self, response):
        total_matches = response.meta.get('total_matches')

        if not total_matches:
            total_matches = self._scrape_total_matches(response)
            response.meta['total_matches'] = total_matches

        # Request next link first
        request = self._scrape_next_results_page_link(response)
        if isinstance(request, Request):
            yield request
        elif request is not None:
            yield Request(url=request, callback=self.parse, meta=response.meta, headers=self.HEADERS, dont_filter=True)

        # Parse products in current page
        for link in self._scrape_product_links(response):
            # cat_name = response.meta.get('cat_name')
            yield {
                'url' : link,
            }


class BaseProduct(Spider):
    HEADERS = {}
    product_url = None
    product_urls = None

    def __init__(self, product_url=None, product_urls=None, input_file=None, *args, **kwargs):
        self.product_url = product_url

        if isinstance(product_urls, list):
            self.product_urls = product_urls
        else:
            self.product_urls = product_urls.split('|||') if product_urls else []

        if input_file:
            with open(input_file, 'r') as f:
                data = json.load(f)
                f.close()
                self.product_urls += [datum.get('url') for datum in data if datum.get('url')]

        super(BaseProduct, self).__init__(*args, **kwargs)


    def start_requests(self):
        if self.product_url:
            self.product_urls.append(self.product_url)

        if self.product_urls:
            for link in self.product_urls:
                yield Request(url=link, headers=self.HEADERS, dont_filter=True)


class BaseCategory(Spider):

    store_db = False
    def __init__(self, store_db=None, *args, **kwargs):

        # Determine if we have to store categories to database.
        self.store_db = store_db and store_db in ['True', 'true', '1']

        super(BaseCategory, self).__init__(*args, **kwargs)

    def store_database(self, categories):
        pass

    def parse(self, response):
        categories = self.get_categories(response)
        if self.store_db:
            self.store_database(categories)

        return categories

    def get_categories(self, response):
        """
        Scrapes the Category URLS

        :param response: Response
        :return list
        """
        raise NotImplementedError


def identity(x):
    return x

def cond_set_value(item, key, value, conv=identity):
    """Conditionally sets the given value to the given dict.

    The condition is that the key is not set in the item or its value is None.
    Also, the value to be set must not be None.
    """
    if item.get(key) is None and value is not None and conv(value) is not None:
        item[key] = conv(value)

FLOATING_POINT_RGEX = re.compile('\d{1,3}[,\.\d{3}]*\.?\d*')