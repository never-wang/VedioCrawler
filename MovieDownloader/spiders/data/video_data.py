
import sqlite3
import string
conn = sqlite3.connect('example.db')

VIDEO_TYPE_MOVIE = "movie"
VIDEO_TYPE_TV = "tv"

table_name = "VideoData"
column_name = "name"
column_year = "year"
column_type = "type"
column_ygdy_url = "ygdy_url"
column_douban_score = "douban_score"
column_imdb_score = "imdb_score"

cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS " + table_name + "("
               + column_name + " text, "
               + column_year + " integer, "
               + column_type + " text, "
               + column_ygdy_url + " text, "
               + column_douban_score + " real, "
               + column_imdb_score + " real,"
               "CONSTRAINT name_unique UNIQUE (" + column_name + ", " + column_year + ", " + column_type + ")"
               ")")
conn.commit()

class VideoData:
    def __init__(self, name, year, type, ygdy_url, douban_score, imdb_score):
        self.name = name
        self.year = year
        self.type = type
        self.ygdy_url = ygdy_url
        self.douban_score = douban_score
        self.imdb_score = imdb_score

    def save(self):
        cursor = conn.cursor()
        cursor.execute("INSERT into %s VALUES ('%s', %d, '%s', '%s', %f, %f)" %
                       (table_name, self.name, self.year, self.type, self.ygdy_url,
                        self.douban_score, self.imdb_score))
        conn.commit()

def query(self, name, year, type):
    cursor = conn.cursor()
    cursor.execute("Select %s, %s, %s, %s, %s, %s from %s where %s = '%s' and %s = %d and %s = '%s'" %
                   (column_name, column_year, column_type, column_ygdy_url, column_douban_score, column_imdb_score,
                       table_name, column_name, name, column_year, year, column_type, type))
    result = cursor.fetchone()
    return VideoData(name = result[0], year = result[1], type = result[2], ygdy_url=result[3],
                     douban_score=result[4], imdb_score=result[5]) if result != None else None
