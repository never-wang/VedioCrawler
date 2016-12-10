# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItem(scrapy.Item):
    name = scrapy.Field()
    thunder_url = scrapy.Field()
    imdb_score = scrapy.Field()
    douban_score = scrapy.Field()
    year = scrapy.Field()
