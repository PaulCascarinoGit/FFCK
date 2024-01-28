import scrapy
from scrapy import Request
from ..items import CanoeKayakScrapItem

class CanoeKayakSpider(scrapy.Spider):
    name = "canoe_kayak"
    allowed_domains = ["www.ffcanoe.asso.fr"]
    start_urls = ["http://www.ffcanoe.asso.fr/eau_vive/slalom/classement/embarcations/index/page:1/limite:500"]

    def parse(self, response):
        for row in response.css('tr[class="paire"] , tr[class="impaire"]'):
            item = CanoeKayakScrapItem()
            item['Rank'] = self.clean_spaces(row.css('td:nth-child(1)::text').extract_first())
            item['Scratch'] = self.clean_spaces(row.css('td:nth-child(2)::text').extract_first())
            item['Name'] = self.clean_spaces(row.css('td:nth-child(3) a::text').extract_first())
            item['Club'] = self.clean_spaces(row.css('td:nth-child(4) a::text').extract_first())
            item['Boat'] = self.clean_spaces(row.css('td:nth-child(5) a::text').extract_first())
            item['Category'] = self.clean_spaces(row.css('td:nth-child(6) a::text').extract_first())
            item['Year'] = self.clean_spaces(row.css('td:nth-child(7)::text').extract_first())
            item['Division'] = self.clean_spaces(row.css('td:nth-child(8)::text').extract_first())
            item['Points_Club'] = self.clean_spaces(row.css('td:nth-child(9)::text').extract_first())
            item['Points'] = self.clean_spaces(row.css('td:nth-child(10)::text').extract_first())
            item['Num_Courses'] = self.clean_spaces(row.css('td:nth-child(11)::text').extract_first())
            item['Courses_Nat'] = self.clean_spaces(row.css('td:nth-child(12)::text').extract_first())

            yield item

        # Gérer la pagination
        next_page = response.css('div.paging a.next::attr(href)').extract_first()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)

    def clean_spaces(self, string):
        if string:
            return " ".join(string.split()).strip()
