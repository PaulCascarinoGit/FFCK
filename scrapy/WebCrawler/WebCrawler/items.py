# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class athlete(scrapy.Item):
    Rank = scrapy.Field()
    Scratch = scrapy.Field()
    Name = scrapy.Field()
    Club = scrapy.Field()
    Boat = scrapy.Field()
    Category = scrapy.Field()
    Year = scrapy.Field()
    Division = scrapy.Field()
    Points_Club = scrapy.Field()
    Points = scrapy.Field()
    Num_Courses = scrapy.Field()
    Courses_Nat = scrapy.Field()