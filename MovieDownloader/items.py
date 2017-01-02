# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from MovieDownloader.spiders.data import video_data


class MovieItem(scrapy.Item):
    name = scrapy.Field()
    download_url = scrapy.Field()
    imdb_score = scrapy.Field()
    douban_score = scrapy.Field()
    year = scrapy.Field()
    type = scrapy.Field()
    douban_url = scrapy.Field()
    imdb_url = scrapy.Field()

    def exists(self):
        video = video_data.query(name=self["name"], year=self["year"], type=self["type"])
        return video is not None

    def save(self):
        video = video_data.VideoData(name = self["name"], year=self["year"], type=self["type"],
                                     download_url= self["download_url"], douban_score = self["douban_score"],
                                     douban_url = self["douban_url"], imdb_score = self["imdb_score"],
                                     imdb_url = self["imdb_url"])
        video.save()
