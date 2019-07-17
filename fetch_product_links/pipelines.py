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
from scrapy.exceptions import DropItem

class FetchProductLinksPipeline(object):

    def process_item(self, item, spider):
        return item

   