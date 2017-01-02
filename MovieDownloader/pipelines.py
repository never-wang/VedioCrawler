# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
from scrapy.exceptions import DropItem


class MoviePipeline(object):
    def open_spider(self, spider):
        self.movies = dict()

    def close_spider(self, spider):
        movieList = []
        wrong_movie_list = []
        for (name, item) in self.movies.iteritems():
            item.save()
            qualified = False
            wrong = False
            for (key, min_score) in [("imdb_score", 7), ("douban_score", 7)]:
                if (key not in item):
                    wrong = True
                if (key in item) and (int(item[key]) >= min_score):
                    qualified = True

            if not qualified:
                movieList.append(item)
            if wrong:
                wrong_movie_list.append(item)
        output = open(time.strftime("%d-%m-%Y.txt"), 'w')
        output.write(str(movieList))
        output.close()

        output = open(time.strftime("%d-%m-%Y-wrong.txt"), 'w')
        output.write(str(wrong_movie_list))
        output.close()

        output = open(time.strftime("%d-%m-%Y-test.txt"), 'w')
        output.write(str(self.movies))
        output.close()

    def get_key(self, item):
        return item["name"] + str(item["year"]) + item["type"]

    def process_item(self, item, spider):
        if self.get_key(item) in self.movies:
            existing_item = self.movies[self.get_key(item)]
            for key in ["douban_score", "imdb_score"]:
                if key in item and int(item[key]) > 0:
                    existing_item[key] = item[key]
            for key in ["douban_url", "imdb_url"]:
                if key in item and len(item[key]) > 0:
                    existing_item[key] = item[key]
        else:
            self.movies[self.get_key(item)] = item

        return item
