# -*- coding: utf-8 -*-
import logging
import traceback
import urlparse

import datetime
import scrapy
import scrapy_splash
import urllib
import requests
import sys

from MovieDownloader.items import MovieItem
from MovieDownloader.spiders.data import video_data


class MovieSpider(scrapy.Spider):
    name = "movie"

    ygdy_domain = "http://www.dytt8.net"
    imdb_domain = "http://www.imdb.com"

    allowed_domains = ["dytt8.net", "imdb.com", "douban.com"]

    start_list_urls = [
        ygdy_domain + "/html/gndy/oumei/index.html",
    ]

    custom_settings = {
        'ITEM_PIPELINES': {
            'MovieDownloader.pipelines.MoviePipeline': 300,
        }
    }

    page_url_set = set()
    has_new_movie = False
    count = 0

    def start_requests(self):
        video_data.init()
        for url in self.start_list_urls:
            request = scrapy.Request(url, callback=self.parse_list_page)
            yield request

    def parse_list_page(self, response):
        self.count  += 1
        if self.count > 3:
            return
        self.has_new_movie = False
        self.page_url_set.clear()
        next_page_href = response.xpath(u"//div[@class ='x']//a[.='\u4e0b\u4e00\u9875']/@href").extract()[0]
        movie_urls = response.xpath("//div[@class='co_content8']/ul//a/@href").extract()
        for movie_url in movie_urls:
            if (not movie_url.endswith("index.html")):
                url = urlparse.urljoin(response.url, movie_url)
                self.page_url_set.add(url)
                request = scrapy_splash.SplashRequest(url, self.parse_movie_page)
            # request = scrapy.Request(self.domain + movie_url, callback=self.parse_movie_page)
                request.meta["next_page"] = urlparse.urljoin(response.url, next_page_href)
                request.meta["current_page"] = response.url
                yield request


        # print next_page_href

    def find_value(self, labels, key):
        for label in labels:
            index = label.find(key)
            if index != -1:
                return label[(index + len(key)):].strip()
        return ""

    def do_parse_movie_page(self, response):
        if response.url == "http://www.dytt8.net/html/gndy/dyzz/20161217/52754.html":
            output = open("test.html", "w")
            output.write(response.body)
            output.close()

        contents = response.xpath("//div[@class='co_content8']//p").extract()

        file_name = ""
        year = 0
        startTime = datetime.datetime.now()
        for content in contents:
            labels = content.split("<br>")
            try:
                file_name = self.find_value(labels, u"片　　名")
                self.log(response.url + ", year : " + str(self.find_value(labels, u"年　　代")))
                year = int(self.find_value(labels, u"年　　代"))
                if (len(file_name) > 0):
                    break
            except:
                pass

        self.log("fuck use time : " + str(datetime.datetime.now() - startTime))
        if len(file_name) == 0:
            self.log("Movie name is empty : " + response.url, logging.WARNING)
            return None, None
        if (year == 0):
            self.log("Movie year is zero : " + response.url, logging.WARNING)
        download_url = \
            response.xpath("//div[@class='co_content8']//div[@id='Zoom']//table/tbody//a/@thunderrestitle").extract()[0]
        meta = dict()

        item = MovieItem(name=file_name, download_url=download_url, year=year, type=video_data.VIDEO_TYPE_MOVIE)
        if not item.exists():
            meta['item'] = item

            try:
                search_url = "https://api.douban.com/v2/movie/search?q=" + urllib.quote_plus(file_name)
                douban_response = requests.get(search_url)
                self.parse_douban_score(douban_response, item)
            except Exception, e:
                traceback.print_exception(*sys.exc_info())

            search_url = "http://www.imdb.com/find?q=" + urllib.quote_plus(file_name) + "&s=tt&ref_=fn_tt"
            return scrapy.Request(url=search_url, callback=self.parse_imdb_search, meta=meta), item

        return None, None

    def parse_movie_page(self, response):

        try:
            (item, request) = self.do_parse_movie_page(response)
            if item is not None:
                self.has_new_movie = True
                yield item
            if request is not None:
                yield request
        except Exception, e:
            traceback.print_exception(*sys.exc_info())

        self.page_url_set.remove(response.url)
        if len(self.page_url_set) == 0 and self.has_new_movie:
            yield scrapy.Request(url=response.meta["next_page"], callback=self.parse_list_page)

    def parse_imdb_search(self, response):
        hrefs = response.xpath("//div[@class='findSection']//td[@class='result_text']/a/@href").extract()
        if len(hrefs) > 0 :
            href = hrefs.pop(0)
            response.meta["hrefs"] = hrefs
            yield scrapy.Request(url=urlparse.urljoin(response.url, href), callback=self.parse_imdb_score, meta=response.meta)

    def parse_imdb_score(self, response):
        imdb_url = urlparse.urlsplit(response.url).geturl()

        imdb_dict = dict()
        try:
            title = response.xpath("//h1[@itemprop='name']/text()").extract().strip()
            imdb_dict['title'] = title
        except Exception:
            pass
        try:
            year = response.xpath("//h1[@itemprop='name']/span/a/text()").extract().strip()
            imdb_dict['year'] = year
        except Exception:
            pass
        item = response.meta['item']
        if self.match(imdb_dict, "title", item, "name") and self.match(imdb_dict, "year", item, "year"):
            score = response.xpath("//div[@class='ratings_wrapper']//span[@itemprop='ratingValue']/text()").extract()[0]
            item['imdb_score'] = float(score)
            item['imdb_url'] = imdb_url
            yield item
        else:
            hrefs = response.meta["hrefs"]
            if len(hrefs) > 0:
                href = hrefs.pop(0)
                response.meta["hrefs"] = hrefs
                yield scrapy.Request(url="http://www.imdb.com" + href, callback=self.parse_imdb_score,
                                      meta=response.meta)

    def parse_douban_score(self, response, item):
        try :
            json_response = response.json()
            subjects = json_response["subjects"]
            for subject in subjects:
                if self.match(subject, "original_title", item, "name") and self.match(subject, "year", item, "y"):
                    score = subject["rating"]["average"]
                    item['douban_score'] = float(score)
                    item['douban_url'] = subject["alt"]
                    return
        except Exception, e:
            self.log(e, logging.ERROR)

    def match(self, subject, subject_key, item, item_key):
        if (not subject_key in subject) or (not item_key in item):
            return True
        return (str(subject[subject_key]) == str(item[item_key]) or
                str(subject[subject_key]).find(str(item[item_key])) != -1 or
                str(str(item[item_key])).find(subject[subject_key]) != -1)
    # def parse_douban_score(self, response):

