# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2
import json
import os
from scrapy.exporters import JsonItemExporter
import os
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem


class FetchProductLinksPipeline(object):
    def __init__(self):
        # self.host = '192.168.0.114'
        self.host = '216.108.230.9'
        # self.host = 'localhost'
        self.username = 'postgres'
        self.password = 'root'
        self.db = 'panda_db'
        self.port = '5432'
        self.cursor = self.connect_db()

    def connect_db(self):
        cnx = {'host': self.host,
               'username': self.username,
               'password': self.password,
               'db': self.db,
               'port': int(self.port)
               }
        self.conn = psycopg2.connect(dbname=cnx['db'], host=cnx['host'], port=cnx['port'], user=cnx['username'],
                                     password=cnx['password'])
        self.cursor = self.conn.cursor()
        return self.cursor

    def process_item(self, item, spider):
        sku = item.get('sku') if item.get('sku') else None
        seller_en = item.get('seller_en') if item.get('seller_en') else None
        price_history = item.get('price_history') if item.get('price_history') else None
        variants = item.get('variants') if item.get('variants') else None

        id, current_price_history = self._compare_price(price_history, seller_en, sku, variants)
        if id:
            item = self._update_product(item, id, current_price_history)
        else:
            item = self._insert_product(item)

        return item

    # Update the existing product data
    def _update_product(self, item, id, current_price_history):
        items = self._parse_items(item)

        if current_price_history:
            price_history = current_price_history
        try:
            sql = "UPDATE product_product SET title=%s, product_description=%s, sku=%s, url=%s, image_url=%s, brand=%s, " \
                  "brand_logo=%s, scraped_results_per_page=%s, price_history=%s, price=%s, quantity=%s, specifications=%s, ranking=%s, " \
                  "average_rating=%s, variants=%s, coupon=%s, value_added_service=%s, remaining_quantity=%s, " \
                  "cummulative_evaluation=%s, purchase=%s, product_set=%s, product_setlist=%s, weight=%s, add_purchase=%s, " \
                  "after_sales_service=%s, shopping_ideas=%s, pickup_shop=%s, effective_time=%s, origin_price=%s, " \
                  "insurance_service=%s, tips=%s, delivery=%s, delivery_service=%s, promotion=%s, value_added_protection=%s, " \
                  "jd_service=%s, plus_special_member_price=%s, service_support=%s, book_ranking=%s, intention_gold=%s, " \
                  "intention_total_price=%s, intention_sales_status=%s, intention_address=%s, recent_opening=%s, certificate_number=%s, " \
                  "intention_tel=%s, price_spike=%s, discount_time=%s, tax=%s, freight=%s, deposit_price=%s, earnest_price=%s, " \
                  "last_price=%s, delivery_date=%s, payment_method=%s, brand_official_website=%s, bundle_savings=%s, " \
                  "abroad_product=%s, prime_service=%s, mechant_id=%s, new_product=%s, cummulative_rate=%s, warranty_service=%s, " \
                  "special_color=%s, departure_country=%s, inventory=%s, voucher=%s, author=%s, publisher=%s, publish_date=%s, " \
                  "price_zhe=%s, paper_price=%s, e_book_price=%s, fighting_price=%s, vip_price=%s, word_count=%s, classification=%s, " \
                  "book_status=%s, book_reading_count=%s, seller_en=%s, seller_ch=%s, keywords=%s, stock_status=%s, discount_product=%s, " \
                  "related_products=%s, category_id=%s, video_url=%s " \
                  "WHERE id=%s"

            self.cursor.execute(sql, (
                items['title'], items['product_description'], items['sku'], items['url'], items['image_url'],
                items['brand'], items['brand_logo'], items['scraped_results_per_page'], price_history,
                items['price'], items['quantity'], items['specifications'], items['ranking'], items['average_rating'],
                items['variants'], items['coupon'], items['value_added_service'], items['remaining_quantity'],
                items['cummulative_evaluation'], items['purchase'], items['product_set'], items['product_setlist'], items['weight'],
                items['add_purchase'], items['after_sales_service'], items['shopping_ideas'], items['pickup_shop'], items['effective_time'],
                items['origin_price'], items['insurance_service'], items['tips'], items['delivery'],
                items['delivery_service'], items['promotion'], items['value_added_protection'], items['jd_service'],
                items['plus_special_member_price'], items['service_support'], items['book_ranking'], items['intention_gold'],
                items['intention_total_price'], items['intention_sales_status'], items['intention_address'], items['recent_opening'],
                items['certificate_number'], items['intention_tel'], items['price_spike'], items['discount_time'], items['tax'], items['freight'],
                items['deposit_price'], items['earnest_price'], items['last_price'], items['delivery_date'],
                items['payment_method'], items['brand_official_website'], items['bundle_savings'], items['abroad_product'],
                items['prime_service'], items['mechant_id'], items['new_product'], items['cummulative_rate'], items['warranty_service'],
                items['special_color'], items['departure_country'], items['inventory'], items['voucher'], items['author'], items['publisher'],
                items['publish_date'], items['price_zhe'], items['paper_price'], items['e_book_price'],
                items['fighting_price'], items['vip_price'], items['word_count'], items['classification'], items['book_status'],
                items['book_reading_count'], items['seller_en'], items['seller_ch'], items['keywords'], items['stock_status'],
                items['discount_product'], items['related_products'], items['category_id'], items['video_url'], id))

            self.conn.commit()

        except Exception as e:
            print (e, 'when update the product data')
        return item

    # Insert to product a new data
    def _insert_product(self, item):
        items = self._parse_items(item)
        try:
            sql = "INSERT INTO product_product (title, product_description, sku, url, image_url, brand, brand_logo, " \
                  "scraped_results_per_page, price_history, price, quantity, specifications, ranking, " \
                  "average_rating, variants, coupon, value_added_service, remaining_quantity, " \
                  "cummulative_evaluation, purchase, product_set, product_setlist, weight, add_purchase, after_sales_service, " \
                  "shopping_ideas, pickup_shop, effective_time, origin_price, insurance_service, tips, delivery, delivery_service, " \
                  "promotion, value_added_protection, jd_service, plus_special_member_price, service_support, book_ranking, " \
                  "intention_gold, intention_total_price, intention_sales_status, intention_address, recent_opening, " \
                  "certificate_number, intention_tel, price_spike, discount_time, tax, freight, deposit_price, earnest_price, " \
                  "last_price, delivery_date, payment_method, brand_official_website, bundle_savings, abroad_product, prime_service, " \
                  "mechant_id, new_product, cummulative_rate, warranty_service, special_color, departure_country, inventory, voucher, " \
                  "author, publisher, publish_date, price_zhe, paper_price, e_book_price, fighting_price, vip_price, word_count, " \
                  "classification, book_status, book_reading_count, seller_en, seller_ch, keywords, stock_status, discount_product, " \
                  "related_products, category_id, video_url) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                  "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                  "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                  "%s, %s, %s, %s, %s, %s, %s, %s, %s)"

            self.cursor.execute(sql, (
                items['title'], items['product_description'], items['sku'], items['url'], items['image_url'],
                items['brand'], items['brand_logo'], items['scraped_results_per_page'], items['price_history'], items['price'],
                items['quantity'], items['specifications'], items['ranking'], items['average_rating'], items['variants'],
                items['coupon'], items['value_added_service'], items['remaining_quantity'], items['cummulative_evaluation'],
                items['purchase'], items['product_set'], items['product_setlist'], items['weight'], items['add_purchase'],
                items['after_sales_service'], items['shopping_ideas'], items['pickup_shop'], items['effective_time'],
                items['origin_price'], items['insurance_service'], items['tips'], items['delivery'], items['delivery_service'],
                items['promotion'], items['value_added_protection'], items['jd_service'], items['plus_special_member_price'],
                items['service_support'], items['book_ranking'], items['intention_gold'], items['intention_total_price'],
                items['intention_sales_status'], items['intention_address'], items['recent_opening'], items['certificate_number'],
                items['intention_tel'], items['price_spike'], items['discount_time'], items['tax'], items['freight'],
                items['deposit_price'], items['earnest_price'], items['last_price'], items['delivery_date'], items['payment_method'],
                items['brand_official_website'], items['bundle_savings'], items['abroad_product'], items['prime_service'],
                items['mechant_id'], items['new_product'], items['cummulative_rate'], items['warranty_service'], items['special_color'],
                items['departure_country'], items['inventory'], items['voucher'], items['author'], items['publisher'],
                items['publish_date'], items['price_zhe'], items['paper_price'], items['e_book_price'], items['fighting_price'],
                items['vip_price'], items['word_count'], items['classification'], items['book_status'], items['book_reading_count'],
                items['seller_en'], items['seller_ch'], items['keywords'], items['stock_status'], items['discount_product'],
                items['related_products'], items['category_id'], items['video_url']
            ))

            self.conn.commit()

        except Exception as e:
            print (e, 'when save the product data')
        return item

    # Compare the price
    def _compare_price(self, price_history, seller, sku, variants):
        id = None
        current_price_history = None
        previous_price_history = None
        if variants:
            sql = "SELECT id, price_history FROM product_product WHERE seller_en=%s AND sku=%s AND variants=%s"
        else:
            sql = "SELECT id, price_history FROM product_product WHERE seller_en=%s AND sku=%s"
        try:
            if variants:
                self.cursor.execute(sql, (seller, sku, variants, ))
            else:
                self.cursor.execute(sql, (seller, sku, ))
            response = self.cursor.fetchall()
            if response:
                resp = response[0]
                id = resp[0]
                previous_price_history = resp[1]

            if previous_price_history and price_history:
                price_history = json.loads(price_history)
                current_price_history = price_history + previous_price_history
            elif previous_price_history:
                current_price_history = previous_price_history
            elif price_history:
                current_price_history = json.loads(price_history)

        except Exception as e:
            print(e, 'when compare the price')

        current_price_history = json.dumps(current_price_history) if current_price_history else None
        return id, current_price_history

    # Parse Item
    def _parse_items(self, item):
        items = {}
        items['title'] = item.get('title') if item.get('title') else None
        items['product_description'] = item.get('product_description') if item.get('product_description') else None
        items['sku'] = item.get('sku') if item.get('sku') else None
        items['url'] = item.get('url') if item.get('url') else None
        items['image_url'] = item.get('image_url') if item.get('image_url') else None
        items['brand'] = item.get('brand') if item.get('brand') else None
        items['brand_logo'] = item.get('brand_logo') if item.get('brand_logo') else None
        items['scraped_results_per_page'] = item.get('scraped_results_per_page') if item.get(
            'scraped_results_per_page') else None

        items['quantity'] = item.get('quantity') if item.get('quantity') else None
        items['specifications'] = item.get('specifications') if item.get('specifications') else None
        items['ranking'] = item.get('ranking') if item.get('ranking') else None
        items['variants'] = item.get('variants') if item.get('variants') else None
        items['coupon'] = item.get('coupon') if item.get('coupon') else None
        items['value_added_service'] = item.get('value_added_service') if item.get('value_added_service') else None

        # items['independent'] = item.get('independent') if item.get('independent') else None

        items['remaining_quantity'] = item.get('remaining_quantity') if item.get('remaining_quantity') else None
        items['cummulative_evaluation'] = item.get('cummulative_evaluation') if item.get(
            'cummulative_evaluation') else None  # review total
        items['average_rating'] = item.get('average_rating') if item.get('average_rating') else None
        items['purchase'] = item.get('purchase') if item.get('purchase') else None
        items['product_set'] = item.get('set') if item.get('set') else None
        items['product_setlist'] = item.get('set_list') if item.get('set_list') else None
        items['weight'] = item.get('weight') if item.get('weight') else None
        items['add_purchase'] = item.get('add_purchase') if item.get('add_purchase') else None

        items['after_sales_service'] = item.get('after_sales_service') if item.get('after_sales_service') else None

        items['shopping_ideas'] = item.get('shopping_ideas') if item.get('shopping_ideas') else None
        items['pickup_shop'] = item.get('pickup_shop') if item.get('pickup_shop') else None
        items['effective_time'] = item.get('effective_time') if item.get('effective_time') else None
        # items['service_type'] = item.get('service_type') if item.get('service_type') else None
        # items['service_store'] = item.get('service_store') if item.get('service_store') else None
        items['origin_price'] = item.get('origin_price') if item.get('origin_price') else None
        items['insurance_service'] = item.get('insurance_service') if item.get('insurance_service') else None

        # JingDong Items
        items['tips'] = item.get('tips') if item.get('tips') else None
        items['delivery'] = item.get('delivery') if item.get('delivery') else None
        items['delivery_service'] = item.get('delivery_service') if item.get('delivery_service') else None

        items['promotion'] = item.get('promotion') if item.get('promotion') else None
        items['value_added_protection'] = item.get('value_added_protection') if item.get(
            'value_added_protection') else None
        items['jd_service'] = item.get('jd_service') if item.get('jd_service') else None

        items['plus_special_member_price'] = item.get('plus_special_member_price') if item.get(
            'plus_special_member_price') else None
        items['service_support'] = item.get('service_support') if item.get('service_support') else None
        items['book_ranking'] = item.get('book_ranking') if item.get('book_ranking') else None
        items['intention_gold'] = item.get('intention_gold') if item.get('intention_gold') else None
        items['intention_total_price'] = item.get('intention_total_price') if item.get(
            'intention_total_price') else None
        items['intention_sales_status'] = item.get('intention_sales_status') if item.get(
            'intention_sales_status') else None
        items['intention_address'] = item.get('intention_address') if item.get('intention_address') else None
        items['recent_opening'] = item.get('recent_opening') if item.get('recent_opening') else None
        items['certificate_number'] = item.get('certificate_number') if item.get('certificate_number') else None
        items['intention_tel'] = item.get('intention_tel') if item.get('intention_tel') else None
        items['price_spike'] = item.get('price_spike') if item.get('price_spike') else None
        items['discount_time'] = item.get('discount_time') if item.get('discount_time') else None
        items['tax'] = item.get('tax') if item.get('tax') else None
        items['freight'] = item.get('freight') if item.get('freight') else None
        items['deposit_price'] = item.get('deposit_price') if item.get('deposit_price') else None
        items['earnest_price'] = item.get('earnest_price') if item.get('earnest_price') else None

        # Amazon CN
        items['last_price'] = item.get('last_price') if item.get('last_price') else None

        items['delivery_date'] = item.get('delivery_date') if item.get('delivery_date') else None
        items['payment_method'] = item.get('payment_method') if item.get('payment_method') else None
        items['brand_official_website'] = item.get('brand_official_website') if item.get(
            'brand_official_website') else None

        items['bundle_savings'] = item.get('bundle_savings') if item.get('bundle_savings') else None
        items['abroad_product'] = item.get('abroad_product') if item.get('abroad_product') else None

        items['prime_service'] = item.get('prime_service') if item.get('prime_service') else None
        items['mechant_id'] = item.get('mechant_id') if item.get('mechant_id') else None
        items['new_product'] = item.get('new_product') if item.get('new_product') else None

        # YHD
        items['cummulative_rate'] = item.get('cummulative_rate') if item.get('cummulative_rate') else None

        # Gome
        items['warranty_service'] = item.get('warranty_service') if item.get('warranty_service') else None
        items['special_color'] = item.get('special_color') if item.get('special_color') else None

        # M18
        items['departure_country'] = item.get('departure_country') if item.get('departure_country') else None
        items['inventory'] = item.get('inventory') if item.get('inventory') else None
        items['voucher'] = item.get('voucher') if item.get('voucher') else None

        # Dangdang
        items['author'] = item.get('author') if item.get('author') else None
        items['publisher'] = item.get('publisher') if item.get('publisher') else None
        items['publish_date'] = item.get('publish_date') if item.get('publish_date') else None
        items['price_zhe'] = item.get('price_zhe') if item.get('price_zhe') else None
        items['paper_price'] = item.get('paper_price') if item.get('paper_price') else None
        items['e_book_price'] = item.get('e_book_price') if item.get('e_book_price') else None
        items['fighting_price'] = item.get('fighting_price') if item.get('fighting_price') else None
        items['vip_price'] = item.get('vip_price') if item.get('vip_price') else None
        items['word_count'] = item.get('word_count') if item.get('word_count') else None
        items['classification'] = item.get('classification') if item.get('classification') else None
        items['book_status'] = item.get('book_status') if item.get('book_status') else None
        items['book_reading_count'] = item.get('book_reading_count') if item.get('book_reading_count') else None

        items['seller_en'] = item.get('seller_en') if item.get('seller_en') else None
        items['seller_ch'] = item.get('seller_ch') if item.get('seller_ch') else None
        items['keywords'] = item.get('keywords') if item.get('keywords') else None
        items['stock_status'] = item.get('stock_status')
        items['price'] = item.get('price') if item.get('price') else None
        items['price_history'] = item.get('price_history') if item.get('price_history') else None
        items['discount_product'] = item.get('discount_product') if item.get('discount_product') else None
        items['related_products'] = item.get('related_products') if item.get('related_products') else None
        items['category_id'] = item.get('category_id') if item.get('category_id') else None
        items['video_url'] = item.get('video_url') if item.get('video_url') else None

        return items


class ProductLinkPipeline(object):
    def open_spider(self, spider):
        self.exporters = {}

    def close_spider(self, spider):
        for exporter in self.exporters.values():
            exporter.finish_exporting()
            exporter.file.close()
    
    def process_item(self, item, spider):
        cat_name = item.get('cat_name')
        if cat_name and spider.output_directory:
            if not os.path.isdir(spider.output_directory):
                os.mkdir(spider.output_directory)
            item.pop('cat_name')
            if cat_name not in self.exporters:
                f = open('{}/{}.json'.format(spider.output_directory, cat_name), 'wb')
                exporter = JsonItemExporter(f)
                exporter.start_exporting()
                self.exporters[cat_name] = exporter

            self.exporters[cat_name].export_item(item)

        return item


class DownloadImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        try:
            image_links = json.loads((item['image_links']))
        except:
            yield None
        else:
            for idx, image_url in enumerate(image_links):
                if image_url.startswith('http'):
                    yield scrapy.Request(image_url, meta={'folder_name': item['title'], 'image_idx': idx})

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item
    #
    # def file_path(self, request, response=None, info=None):
    #     return '{}/image{}.jpg'.format(request.meta['folder_name'], request.meta['image_idx'])
