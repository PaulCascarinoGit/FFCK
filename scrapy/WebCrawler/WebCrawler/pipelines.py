# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
#from itemadapter import ItemAdapter
from pymongo import MongoClient

class WebcrawlerPipeline:
    collection = 'ffck_collection'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()


    def process_item(self, item, spider):
        '''
        On supprime les tab et sauts de lignes
        '''
        # Nettoyer les valeurs
        for field in item.fields:
            value = item.get(field)
            if value is not None and not isinstance(value, int) and not isinstance(value, float) :
                if not value.replace(".", "").replace("-", "").isdigit():
                    item[field] = value.replace('\t', '').replace('\n', '').replace("'", '').strip()
                else:
                    item[field] = float(value.replace('\t', '').replace('\n', '').strip())
        self.db[self.collection].insert_one(dict(item))
        return item

    
