# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class athlete(scrapy.Item):
    Rank = scrapy.Field()
    Scratch = scrapy.Field()
    Nom = scrapy.Field()
    Prenom = scrapy.Field()
    Club = scrapy.Field()
    Embarcation = scrapy.Field()    
    Sexe = scrapy.Field()
    Categorie = scrapy.Field()
    Annee = scrapy.Field()
    Division = scrapy.Field()
    Points_Club = scrapy.Field()
    Moyenne = scrapy.Field()
    Nombre_de_courses = scrapy.Field()
    Nombre_de_courses_nationales = scrapy.Field()