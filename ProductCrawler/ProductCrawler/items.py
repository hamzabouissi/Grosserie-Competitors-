# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    description = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    barcode = scrapy.Field()
    category = scrapy.Field()
    created_at = scrapy.Field()

class PriceLogs(scrapy.Item):
    
    product_barcode = scrapy.Field()
    price = scrapy.Field()
    source = scrapy.Field()
    # Link = scrapy.Field()
    created_at = scrapy.Field()
