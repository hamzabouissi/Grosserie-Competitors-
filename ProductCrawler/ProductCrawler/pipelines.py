# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from .items import ProductItem,PriceLogs

class ProductcrawlerPipeline(object):
    
    
    def process_item(self, item, spider):
        return item


class MongoPipeline(object):
    
    collection_name = 'products'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'Crawler')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    # def process_item(self, item, spider):
    #     item = dict(item)
    #     item_source  = item['sources'][0]
    #     product = self.db[self.collection_name].find_one({"barcode":item['barcode']})
    #     if product:
    #         for source in product['sources']:
    #             if source['name'] == item_source['name']:
    #                 if source['price'] != item_source['price']:
    #                     source['price'] = item_source['price']
    #                     self.db[self.collection_name].update_one(
    #                         {"barcode":item['barcode']},
    #                         {"$set":{"sources":  product['sources'] }}
    #                     )
    #                 return item
                   
    #         self.db[self.collection_name].update_one(
    #             {"barcode":item['barcode']},
    #             { "$addToSet": { 
    #                     "sources": item_source
    #                 }
    #             }
    #         )
    #     else:
    #         self.db[self.collection_name].insert_one(item)
    #     return item
    
    def process_item(self, item, spider):

        if isinstance(item,ProductItem) :
            exist = self.db['Products'].find_one({"barcode":item['barcode']})
            if not exist:
                self.db["Products"].insert_one(dict(item))
        elif isinstance(item,PriceLogs):
            exist = self.db['PriceLogs'].find_one(
                {
                    "product_barcode":item["product_barcode"],
                    "price":item['price'],
                    "source":item['source']
                }
            )
            if not exist:
                self.db["PriceLogs"].insert_one(dict(item))
        
        return item