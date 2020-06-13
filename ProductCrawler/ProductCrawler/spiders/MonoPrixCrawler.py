import scrapy
from bs4 import BeautifulSoup
import re
import requests
import asyncio
import aiohttp
import queue
from datetime import datetime
from ProductCrawler.pipelines import MongoPipeline
from ProductCrawler.items import ProductItem,PriceLogs

class MonoPrixCrawler(scrapy.Spider):

    name = 'MonoPrix'
    start_urls = [
        "https://clickandcollect.monoprix.tn/soussemaghrebarabe/"
    ]
    def GetProductsInfo(self,response):
        q = queue.Queue()
        
        page = BeautifulSoup(response.text,"lxml")
        products = page.find_all("div",class_="product-miniature js-product-miniature")
        _ids = []
        for product in products:
            _ids.append(product.attrs['data-id-product'])
        
        asyncio.run(self.addProductsToCart(_ids,q))
        
        while not q.empty():
            yield q.get(block=True)

        next_page = page.find("a",attrs={'rel':"next"})
        if next_page:
            link = next_page.attrs['href']
            yield scrapy.Request(url = link,callback=self.GetProductsInfo)
    
        

    def RequestNewCookies(self):
        resp  = requests.get("https://clickandcollect.monoprix.tn/soussemaghrebarabe",verify=False)
        return resp.cookies
    
    async def addProductsToCart(self,ids,queue):
        cookies = self.RequestNewCookies()
        phpseesid = cookies['PHPSESSID']
        prestashop = cookies['PrestaShop-361e4668932f6ee98e3bc2125a162420']

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            data = await asyncio.gather(*[
                self.fetch(session,id,phpseesid,prestashop,queue)
                for id in ids
            ])


    async def fetch(self,client,id,phpseesid,prestashop,queue):
        # PHPSESSID=va5d490t8q6q59ab1c14cfs704; PrestaShop-418355ccbf988130449281ed8716f166=def50200c15305d04c45f10ca803fdc1c6e31e83ab2f9d929c3c4a43c6804ec902e9baca39cb9bc8d07c640edb6649dfa3b79725df3469efd9dbae820cc735348d0450874bcf4b45c867d44f84ba8a3376db1da589f95d9537acf8d418f47d4bd8d807d89ca837f973cf222af263d47bfd9e2cadd6bc894da3895c4b42447998b551ee40c79a111504fdecd9ddba7334dbd6ae77650fdb341416132b8b7ec022b7c3fe3d723306492999378aa259bb9b237705c4ea0e79f7199b0219d550effe2d27ec10cba4ff7f992cd81151355e270a344d7a47aa98097a13
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cookie': f'PHPSESSID={phpseesid}; PrestaShop-361e4668932f6ee98e3bc2125a162420={prestashop}'
        }
        payload = {
            'id_product': int(id),
            'qty': '1',
            'add': '1',
            'action': 'update'
        }
        async with client.request('post','https://clickandcollect.monoprix.tn/soussemaghrebarabe/panier',data=payload,headers=headers) as resp:
            
            assert resp.status == 200
            data =  await resp.json(content_type=None)
            try:
                products = data['cart']["products"]
            except KeyError:
                self.logger.error(f"Error Item : {int(id)}")
            for product in products:
                if product['id_product'] == id:
                    break
            try:
                product_image = product['images'][0]['medium']['url']
            except IndexError:
                product_image = "https://www.w4ter.co.za/error.png"
            self.logger.info(f"Crawled Item : {product['name']}")
            
            item = ProductItem()

            item['barcode'] = int(product['ean13'])
            item['category'] =  product['category']
            item['title'] =  product['name']
            item['description'] = product['description_short']
            item['image_urls'] =  [product_image]
            item['created_at'] = datetime.now()
            
            Price = PriceLogs()
            Price['product_barcode'] = product['ean13']
            Price["price"] = product['price_without_reduction']
            Price['source'] = "MonoPrix"
            Price['created_at'] = datetime.now()
            
            queue.put(item)
            queue.put(Price)
            # yield item
        
       
      

    def parse(self,response):
        page = BeautifulSoup(response.text,"lxml")
        categories = page.find_all("a",class_="dropdown-item",attrs={'data-depth':0})
        for cate in categories[1:]:
            link = cate.attrs['href']
            yield scrapy.Request(url = link,callback=self.GetProductsInfo)