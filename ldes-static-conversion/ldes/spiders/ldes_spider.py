import scrapy
import re

from urllib.parse import unquote, urlparse, parse_qsl

from typing import TYPE_CHECKING, Any, List
from scrapy.spiders import Spider

from scrapy.utils.python import unique as unique_list
from scrapy.utils.response import get_base_url
from scrapy.utils.project import get_project_settings

from rdflib import Graph
from ldes.items import LdesFragmentItem


class LdesSpider(Spider):
    name = 'ldes-spider'

    # Pass settings to pipeline through spider
    base_path : str = None
    ldes_start_node : str = None
    fragments_output_dir : str = None
    
    custom_settings = {
        'ITEM_PIPELINES': {
            "ldes.pipelines.RDFWriterPipeline": 200,
        }
    }

    def __init__(self, name: str | None = None, **kwargs: Any):
        self.base_path = get_project_settings().get('LDES_BASE_PATH')
        self.ldes_start_node = get_project_settings().get('LDES_START_NODE')
        self.fragments_output_dir = get_project_settings().get('FRAGMENTS_OUTPUT_DIR')

        if not hasattr(self, "start_urls"):
            self.logger.debug("STARTING FROM <%s>.", self.ldes_start_node)
            self.start_urls = [self.ldes_start_node]
        if not hasattr(self, "allowed_domains"):
            domain = urlparse(self.ldes_start_node).netloc
            self.logger.debug("DOMAIN LOCKED TO <%s>.", domain)
            self.allowed_domains = [domain]
        super().__init__(name, **kwargs)

    def parse(self, response):
        self.logger.debug("HIT------------------------------>")
        content_type = re.search(r"^([^;]*)", str(response.headers["Content-Type"].decode())).group(0)
        
        graph = Graph()
        graph.parse( data=response.body, format=content_type, publicID=response.url)
        # Follow tree:relations
        relations_query = """
            PREFIX tree: <https://w3id.org/tree#>
            SELECT DISTINCT ?relation
            WHERE {
                ?node tree:relation/tree:node ?relation.
            }"""

        relations_query_result = graph.query(relations_query)
        for row in relations_query_result:
            yield scrapy.Request(row.relation)

        # Create item from document
        yield LdesFragmentItem(graph=graph, url=response.url, headers=response.headers)




    

