
import scrapy
from bs4 import BeautifulSoup
import re
from ProductCrawler.items import ProductItem

class MantoojProductCrawler(scrapy.Spider):

    name = 'MantoojProduct'
    start_urls = [
        "https://www.mantooj.net/index.php?option=com_content&view=article&id=4&Itemid=137&lang=fr"
    ]


    def GetProductInfo(self,response):
        page = BeautifulSoup(response.text,"lxml")
        info = page.find("div",class_="text-produit")
        description = info.find_all("p",class_='categorie-produit')

        image_url = "https://www.mantooj.net/" + page.find("div",class_="logo-produit").select("div > img")[0].attrs['src'].strip()
        title = info.select("h3")[0].get_text().strip()
        barcode = description[0].text.split(" : ")[1]

        product = ProductItem()

        product['image_urls'] = [image_url]
        product['title'] = title
        product['barcode'] = barcode
        # product['sources'] = [
        #     {
        #         "name":"Mantooj",
        #         "price":
        #     }
        # ]
        self.logger.info(f"Crawled Item : {title}")
        yield product

    def FindProductItems(self,response):
        page = BeautifulSoup(response.text,"lxml")
        products = page.find_all("div",class_="detail-search-product")
        for product in products:
            link = product.select("div.text > a")[0]
            yield response.follow(link.attrs['href'],callback=self.GetProductInfo)
            
    
    def parse(self,response):
        # items = response.xpath('//*[@id="segmentN5"]/div[2]/div')
        # print(items)
        page = BeautifulSoup(response.text,"lxml")
        category = page.find("div",id="segmentN5")
        sub_category = category.find_all("div",class_=re.compile("child-classe-listing"))
        for cate in sub_category:
            yield response.follow(cate.next.attrs['href'],callback=self.FindProductItems)
