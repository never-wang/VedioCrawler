import sqlite3
import string

db_name = 'example.db'

conn = None
VIDEO_TYPE_MOVIE = "movie"
VIDEO_TYPE_TV = "tv"

table_name = "VideoData"
column_name = "name"
column_year = "year"
column_type = "type"
column_download_url = "download_url"
column_douban_score = "douban_score"
column_imdb_score = "imdb_score"
column_douban_url = "douban_url"
column_imdb_url = "imdb_url"


class VideoData:
    def __init__(self, name, year, type, download_url, douban_score, douban_url, imdb_score, imdb_url):
        self.name = name
        self.year = year
        self.type = type
        self.download_url = download_url
        self.douban_score = douban_score
        self.douban_url = douban_url
        self.imdb_score = imdb_score
        self.imdb_url = imdb_url

    def save(self):
        cursor = conn.cursor()
        sql = "INSERT into %s VALUES ('%s', %d, '%s', '%s', %f, '%s', %f, '%s')" % \
              (table_name, self.name, self.year, self.type, self.download_url,
               self.douban_score, self.douban_url, self.imdb_score, self.imdb_url)
        cursor.execute(sql)
        conn.commit()

    def __eq__(self, other):
        return (other != None and isinstance(other, VideoData) and
                self.name == other.name and self.year == other.year and self.type == other.type
                and self.download_url == other.download_url and self.douban_score == other.douban_score
                and self.douban_url == other.douban_url and self.imdb_score == other.imdb_score
                and self.imdb_url == other.imdb_url)


def query(name, year, type):
    cursor = conn.cursor()
    cursor.execute("Select %s, %s, %s, %s, %s, %s, %s, %s from %s where %s = '%s' and %s = %d and %s = '%s'" %
                   (column_name, column_year, column_type, column_download_url, column_douban_score, column_douban_url,
                    column_imdb_score, column_imdb_url,
                    table_name, column_name, name, column_year, year, column_type, type))
    result = cursor.fetchone()
    return VideoData(name=result[0], year=result[1], type=result[2], download_url=result[3],
                     douban_score=result[4], douban_url=result[5], imdb_score=result[6], imdb_url=result[7]) \
        if result != None else None

def clear():
    cursor = conn.cursor()
    cursor.execute("Delete from %s" % table_name)
    conn.commit()

def init():
    global conn
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS " + table_name + "("
                   + column_name + " text, "
                   + column_year + " integer, "
                   + column_type + " text, "
                   + column_download_url + " text, "
                   + column_douban_score + " real, "
                   + column_douban_url + " text, "
                   + column_imdb_score + " real,"
                   + column_imdb_url + " text, "
                                      "CONSTRAINT name_unique UNIQUE (" + column_name + ", " + column_year + ", " + column_type + ")"
                                                                                                                                  ")")
    conn.commit()
