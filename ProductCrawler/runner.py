import os
from apscheduler.schedulers.background import BackgroundScheduler
from scrapy.crawler import CrawlerProcess,Crawler
from scrapy.utils.project import get_project_settings
from ProductCrawler.spiders import GeantProductCrawler
from scrapy.utils.project import get_project_settings
import logging,time


os.chdir(os.path.dirname(os.path.realpath(__file__)))


def run():
    process = CrawlerProcess(get_project_settings())
    process.crawl("MonoPrix")
    process.start()
    
run()
