FROM python:3.7.2-stretch


RUN \
apt-get update -qq && \
apt-get install -y \
curl \
virtualenv  \
cron \ 
nano

RUN rm -rf /var/lib/apt/lists/*

ENV SHELL /bin/bash

WORKDIR /home/docker/ProductCrawler
COPY . .
