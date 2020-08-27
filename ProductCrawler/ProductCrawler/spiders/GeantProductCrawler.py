import scrapy
from bs4 import BeautifulSoup
import re,json
import requests
import asyncio
import aiohttp
import queue
from datetime import datetime
from ProductCrawler.pipelines import MongoPipeline
from ProductCrawler.items import ProductItem,PriceLogs

class GeantProductCrawler(scrapy.Spider):

    name = 'Geant'
    start_urls = [
        "https://www.geantdrive.tn/tunis-city/"
    ]
    def GetProductsInfo(self,response):
        
        page = BeautifulSoup(response.text,"lxml")
        # images = []
        # for image in page.find_all("div", class_="wb-image-block"):
        #     images.append(image.a.img)
        
        products = {}
        for i in page.find_all('script', type="text/javascript"): 
            s = str(i.encode('utf-8')) 
            index = s.find("productsListCache") 
            if index != -1: 
                end = s.find(";",index) 
                text  = s[index+20:end].replace("\'","\\'")
                products = json.loads(text) 
                break
        for pr_id,product in products.items():
            pr_id = pr_id.split("-")[0]
            article = page.find("article",attrs={"data-id-product":pr_id})
            image = article.find("div", class_="wb-image-block").a.img
            description = article.find("div",id=f"product-description-short-{pr_id}")

            item = ProductItem()
            item['barcode'] = int(product['ean13'])
            item['category'] =  product['category']
            item['title'] =  product['name']
            item['description'] = description.string
            item['image_urls'] =  [image.attrs['src']]
            item['created_at'] = datetime.now()
            
            Price = PriceLogs()
            Price['product_barcode'] = product['ean13']
            Price["price"] = product['price_amount']
            Price['source'] = "Geant"
            Price['created_at'] = datetime.now()
            yield item
            yield Price
        
        next_page = page.find("a",attrs={'rel':"next"})
        if next_page:
            link = next_page.attrs['href']
            self.logger.info(f"{link}")
            yield scrapy.Request(url = link,callback=self.GetProductsInfo)
    
        

    # def RequestNewCookies(self):
    #     resp  = requests.get("https://www.geantdrive.tn",verify=False)
    #     return resp.cookies
    
    # async def addProductsToCart(self,ids,queue):
    #     cookies = self.RequestNewCookies()
    #     phpseesid = cookies['PHPSESSID']
    #     prestashop = cookies['PrestaShop-a3c7fee44cd16ea27f6813f8566cf6a5']

    #     async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
    #         data = await asyncio.gather(*[
    #             self.fetch(session,id,phpseesid,prestashop,queue)
    #             for id in ids
    #         ])


    # async def fetch(self,client,id,phpseesid,prestashop,queue):
        

    #     headers = {
    #         'Accept': 'application/json, text/javascript, */*; q=0.01',
    #         'Cookie': f'PHPSESSID={phpseesid}; PrestaShop-a3c7fee44cd16ea27f6813f8566cf6a5={prestashop}'
    #     }
    #     payload = {
    #         'id_product': id,
    #         'qty': '1',
    #         'add': '1',
    #         'action': 'update'
    #     }
    #     async with client.request('post','https://www.geantdrive.tn/panier',data=payload,headers=headers) as resp:
            
    #         assert resp.status == 200
    #         data =  await resp.json(content_type=None)
    #         for product in data['cart']["products"]:
    #             if product['id_product'] == id:
    #                 break
    #         try:
    #             product_image = product['images'][0]['medium']['url']
    #         except IndexError:
    #             product_image = "https://www.w4ter.co.za/error.png"
    #         # The added Product get the last index in (Panier)
    #         self.logger.info(f"Crawled Item : {product['name']}")
    #         item = ProductItem()

    #         item['barcode'] = int(product['ean13'])
    #         item['category'] =  product['category']
    #         item['title'] =  product['name']
    #         item['description'] = product['description_short']
    #         item['image_urls'] =  [product_image]
            
    #         item['created_at'] = datetime.now()
            
    #         Price = PriceLogs()
    #         Price['product_barcode'] = product['ean13']
    #         Price["price"] = product['price_without_reduction']
    #         Price['source'] = "Geant"
    #         Price['created_at'] = datetime.now()
            
    #         queue.put(item)
    #         queue.put(Price)
    #         # yield item
        
      

    def parse(self,response):
        page = BeautifulSoup(response.text,"lxml")
        categories = page.find_all("li",class_="level-1 parent")
        for cate in categories:
            link  = cate.find("a").attrs['href']
            yield scrapy.Request(url = link,callback=self.GetProductsInfo)