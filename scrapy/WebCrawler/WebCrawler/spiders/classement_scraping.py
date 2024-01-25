import scrapy
from ..items import ClassementFfckItem

class ClassementFfckSpider(scrapy.Spider):
    name = "classement_ffck"
    start_urls = ["http://www.ffcanoe.asso.fr/eau_vive/slalom/classement/embarcations/index",]

    def parse(self, response):
        for row in response.xpath('//table[@cellpadding="0" and @cellspacing="0"]/tr[@class="paire" or @class="impaire"]'):
            item = ClassementFfckItem()
            item['Rank'] = row.xpath('td[1]/text()').extract_first()
            item['Scratch'] = row.xpath('td[2]/text()').extract_first()
            item['Name'] = row.xpath('td[3]/a/text()').extract_first()
            item['Club'] = row.xpath('td[4]/a/text()').extract_first()
            item['Boat'] = row.xpath('td[5]/a/text()').extract_first()
            item['Category'] = row.xpath('td[6]/a/text()').extract_first()
            item['Year'] = row.xpath('td[7]/text()').extract_first()
            item['Division'] = row.xpath('td[8]/@class').extract_first()
            item['Points_Club'] = row.xpath('td[9]/text()').extract_first()
            item['Points'] = row.xpath('td[10]/text()').extract_first()
            item['Num_Courses'] = row.xpath('td[11]/text()').extract_first()
            item['Courses_Nat'] = row.xpath('td[12]/text()').extract_first()

            yield item
        # Gérer la pagination
        next_page = response.css('div.paging a.next::attr(href)').extract_first()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)