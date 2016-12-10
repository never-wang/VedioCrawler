# -*- coding: utf-8 -*-
import logging

import scrapy
import scrapy_splash
import urllib
import requests

from MovieDownloader.items import MovieItem


class MovieSpider(scrapy.Spider):
    name = "movie"

    ygdy_domain = "http://www.ygdy8.net"
    imdb_domain = "http://www.imdb.com"

    allowed_domains = ["ygdy8.net", "imdb.com", "douban.com"]

    start_urls = [
        "http://www.ygdy8.net/html/gndy/oumei/index.html",
    ]

    custom_settings = {
        'ITEM_PIPELINES': {
            'MovieDownloader.pipelines.MoviePipeline': 300,
        }
    }

    def start_requests(self):
        for url in self.start_urls:
            request = scrapy.Request(url, callback=self.parse_list_page)
            yield request

    def parse_list_page(self, response):
        movie_urls = response.xpath("//div[@class='co_content8']/ul//a/@href").extract()
        for movie_url in movie_urls:
            if (not movie_url.endswith("index.html")):
                request = scrapy_splash.SplashRequest(self.ygdy_domain + movie_url, self.parse_movie_page)
            # request = scrapy.Request(self.domain + movie_url, callback=self.parse_movie_page)
                self.log(request)
                yield request

        # next_page_href = response.xpath(u"//div[@class ='x']/a[.='\u4e0b\u4e00\u9875']").extract()
        # print next_page_href

    def find_value(self, labels, key):
        for label in labels:
            index = label.find(key)
            if index != -1:
                return label[(index + len(key)):].strip()
        return ""

    def parse_movie_page(self, response):
        labels = response.xpath("//div[@class='co_content8']//p").extract()[0].split("<br>")

        file_name = self.find_value(labels, u"片　　名")
        year = int(self.find_value(labels, u"年　　代"))

        if len(file_name) == 0:
            return
        thunder_url = response.xpath("//div[@class='co_content8']//div[@id='Zoom']//table/tbody//a/@thunderrestitle").extract()
        meta = dict()

        item = MovieItem(name = file_name, thunder_url = thunder_url, year = year)
        meta['item'] = item

        search_url="https://api.douban.com/v2/movie/search?q=" + urllib.quote_plus(file_name)
        response = requests.get(search_url)
        self.parse_douban_score(response, item)
        yield item

        search_url = "http://www.imdb.com/find?q=" + urllib.quote_plus(file_name) + "&s=tt&ref_=fn_tt"
        yield scrapy.Request(url=search_url, callback=self.parse_imdb_search, meta=meta)

    def parse_imdb_search(self, response):
        hrefs = response.xpath("//div[@class='findSection']//td[@class='result_text']/a/@href").extract()
        if len(hrefs) > 0 :
            href = hrefs.pop(0)
            response.meta["hrefs"] = hrefs
            yield scrapy.Request(url="http://www.imdb.com" + href, callback=self.parse_imdb_score, meta=response.meta)

    def parse_imdb_score(self, response):
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

