# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class WebcrawlerPipeline:
    def process_item(self, item, spider):
        '''
        On supprime les tab et sauts de lignes
        '''
        # Nettoyer les valeurs
        for field in item.fields:
            value = item.get(field)
            if value is not None:
                if not value.replace(".", "").replace("-", "").isdigit():
                    item[field] = value.replace('\t', '').replace('\n', '').replace("'", '').strip()
                else:
                    item[field] = float(value.replace('\t', '').replace('\n', '').strip())
        return item

    
