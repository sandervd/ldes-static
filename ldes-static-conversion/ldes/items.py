# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LdesFragmentItem(scrapy.Item):
    graph = scrapy.Field()
    url = scrapy.Field()
    headers = scrapy.Field()
