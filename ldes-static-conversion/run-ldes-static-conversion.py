from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from ldes.spiders.ldes_spider import LdesSpider
import os

# Change cwd to script location, so scrapy settings files are picked up.
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

process = CrawlerProcess(get_project_settings())
process.crawl(LdesSpider)
process.start()
