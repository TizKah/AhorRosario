# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CotoScrapItem(scrapy.Item):
    # define the fields for your item here like:
    description = scrapy.Field()
    price = scrapy.Field()
    brand = scrapy.Field()
    image = scrapy.Field()
    market = scrapy.Field()
