import scrapy
from WebCrawler.items import athlete


class ClassementFfckSpider(scrapy.Spider):
    name = "classement_ffck"
    start_urls = ["http://www.ffcanoe.asso.fr/eau_vive/slalom/classement/embarcations/index",]
    custom_date = "28/01/2023"
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 100  # Limiter le spider à 100 items
    }



    def parse(self, response):
        for row in response.xpath('//table[@cellpadding="0" and @cellspacing="0"]/tr[@class="paire" or @class="impaire"]'):
            item = athlete()
            item['Rank'] = int(row.xpath('td[1]/text()').extract_first())
            item['Scratch'] = int(row.xpath('td[2]/text()').extract_first())
            name = row.xpath('td[3]/a/text()').extract_first()
            # Diviser la chaîne en fonction de l'espace
            parts = name.split(" ", 1)
            # Assigner le prénom et le nom à item
            if len(parts) >= 2:
                item['Prenom'] = parts[0]
                item['Nom'] = parts[1]
            else:
                # Gérer le cas où il n'y a qu'un seul mot (prénom sans nom ou vice versa)
                item['Prenom'] = name
                item['Nom'] = ""
            item['Club'] = row.xpath('td[4]/a/text()').extract_first()
            emb_sex =  row.xpath('td[5]/a/text()').extract_first()
            item['Embarcation'] = emb_sex[0:2]
            item['Sexe'] =emb_sex[2]
            item['Categorie'] = row.xpath('td[6]/a/text()').extract_first()
            item['Annee'] = int(row.xpath('td[7]/text()').extract_first())
            item['Division'] = row.xpath('td[8]/text()').extract_first()
            item['Points_Club'] = float(row.xpath('td[9]/text()').extract_first())
            item['Moyenne'] = float(row.xpath('td[10]/text()').extract_first())
            item['Nombre_de_courses'] = int(row.xpath('td[11]/text()').extract_first())
            item['Nombre_de_courses_nationales'] = int(row.xpath('td[12]/text()').extract_first())

            yield item

        # Gérer la pagination
        next_page = response.css('div.paging a.next::attr(href)').extract_first()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)

###data[ClassementEmbarcation][date]