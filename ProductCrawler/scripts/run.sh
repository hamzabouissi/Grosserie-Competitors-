#!/bin/bash
cd /home/docker/ProductCrawler
source env/bin/activate
scrapy crawl $CONTAINER_SCRIPT

