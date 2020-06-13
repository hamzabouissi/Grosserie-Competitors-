import scrapy
from bs4 import BeautifulSoup

from ProductCrawler.items import ProductItem,PriceLogs
from datetime import datetime

def has_class(tag):
    return (tag.name=='a') and (tag.get('class') == ["nav-link"] or tag.get('class') == ["dropdown-item"])


class LivriniSpider(scrapy.Spider):

    name = 'livrini'
    start_urls = [
        "https://livrini.tn/"
    ]
    def GetProductInfo(self,response):
        page = BeautifulSoup(response.text,"lxml")
        extra_data = page.find("div",class_="product-extra-data")
        title = page.find("h1",class_="product-title")
        desc = page.find("div",class_="product-description")
        image_url = page.select("div.product-gallery-image > a")[0].attrs['data-image']
        
        item = ProductItem()
        item['title'] =  title.text.strip()
        item['description'] = desc.text.strip() if desc else ""
        item['barcode'] = int(extra_data.select("p:nth-of-type(1) > span")[0].text)
        item['category'] = extra_data.select("p:nth-of-type(2) > span")[0].text
        item['image_urls'] = [image_url]
        item['created_at'] = datetime.now()
        
        Price = PriceLogs()
        Price['product_barcode'] = item['barcode']
        Price["price"] = page.find("span",class_="solid-price").text
        Price['source'] = "livrini"
        Price['created_at'] = datetime.now()
        
        yield item
        yield Price
    
    def FindProductItems(self,response):
        print(response.url)
        page = BeautifulSoup(response.text,"lxml")
        products = page.find_all("div",class_="product-body")
        for product in products:
            link = product.find("a").attrs['href']
            print(link)

            yield scrapy.Request(url = link,callback=self.GetProductInfo)
        next_page = page.find("a",attrs={'rel':"next"})
        if next_page:
            link = next_page.attrs['href']
            yield scrapy.Request(url = link,callback=self.FindProductItems)
    
    
    def parse(self,response):
        page = BeautifulSoup(response.text,"lxml")
        categories =  page.find_all(has_class)
        for cate in categories:
            link = cate.attrs['href']
            yield scrapy.Request(url = link,callback=self.FindProductItems)
        
