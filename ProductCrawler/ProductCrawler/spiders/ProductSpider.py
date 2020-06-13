import scrapy
from bs4 import BeautifulSoup
import re

from ProductCrawler.items import ProductItem

class ProductSpider(scrapy.Spider):

    name = 'products'
    start_urls = [
        "https://superette.tn/"
    ]

    def GetProductInfo(self,response):
        page = BeautifulSoup(response.text,"lxml")
        
        title = page.find("h1",class_="product-title product_title entry-title")
        price = page.find("span",class_='woocommerce-Price-amount amount')
        description = page.find("div",id="tab-description")
        image = page.find("div",class_='woocommerce-product-gallery__image').find("img")
        barcode = image.attrs['title']  if image.attrs['title'].isdigit() else ''
        image_url = image.attrs['src']
        category  = page.find("nav",class_='woocommerce-breadcrumb breadcrumbs uppercase')
        item = ProductItem()

        item['title'] = title.string.strip()
        item['description'] = description.get_text().strip()
        item['image_urls'] = [image_url]
        item['barcode'] = barcode
        item['category'] = category.get_text()
        item['sources'] = [
            {
                "name":"superette",
                "price":price.get_text().strip()
            }
        ]
        
        yield item
    
    def FindProductItems(self,response):
        page = BeautifulSoup(response.text,"lxml")
        products = page.find_all("p",class_="name product-title")
        for product in products:
            yield scrapy.Request(url = product.next.attrs['href'],callback=self.GetProductInfo)

    def parse(self,response):
        page = BeautifulSoup(response.text,"lxml")
        categories = page.find_all("li",class_=re.compile("nav-dropdown-col"))
        for cate in categories:
            for product in cate.find_all("li"):
                yield scrapy.Request(url = product.next.attrs['href'],callback=self.FindProductItems)