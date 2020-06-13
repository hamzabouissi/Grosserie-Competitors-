import scrapy
from bs4 import BeautifulSoup
import re
import requests
import asyncio
import aiohttp
import queue



class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/3/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url
        self.logger.info(f"Crawler {page}")