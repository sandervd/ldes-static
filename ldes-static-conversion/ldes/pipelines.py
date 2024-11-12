# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import posixpath
from itemadapter import ItemAdapter
from rdflib import RDF, BNode, Graph, Literal, URIRef

from scrapy import Spider
from scrapy.utils.project import get_project_settings
from ldes.items import LdesFragmentItem
import urllib.parse

import os
import shutil

import pprint
from urllib.parse import urljoin, urlunsplit, unquote, urlparse, urlunparse, parse_qsl

# Write the RDF 'page objects' to disk
class RDFWriterPipeline:
    def open_spider(self, spider : Spider):
        # Delete any pre-existing data in export folder.
        for root, dirs, files in os.walk(get_project_settings().get('FRAGMENTS_OUTPUT_DIR')):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
        spider.logger.info("The working fragments working directory has been emptied before crawling starts.")

    def process_item(self, item, spider : Spider):
        if not isinstance(item, LdesFragmentItem):
            return item
        
        adapter = ItemAdapter(item)
        fragment_graph : Graph = adapter.get('graph')
        file_path = self.filepath_for_storage(item=item, spider=spider)
        spider.logger.debug("REWRITING RELATIVE TO DOCUMENT %s", adapter.get('url'))
        relative_graph = self.to_relative_graph(absolute_graph=fragment_graph, base_path=spider.base_path, document_uri=adapter.get('url'))
        
        relative_graph.serialize(format="ttl", destination=file_path)
        return item
    
    def to_relative_graph(self, absolute_graph : Graph, base_path : str, document_uri : str) -> Graph:
        relative_graph = Graph()

        for subj, pred, obj in absolute_graph:
            # Convert subject, predicate and object if they are URIs and start with the base URI
            if isinstance(subj, URIRef) and str(subj).startswith(base_path):
                subj = URIRef(self.to_document_relative_urls(str(subj), document_uri))
            if isinstance(pred, URIRef) and str(pred).startswith(base_path):
                pred = URIRef(self.to_document_relative_urls(str(pred), document_uri))
            if isinstance(obj, URIRef) and str(obj).startswith(base_path):
                obj = URIRef(self.to_document_relative_urls(str(obj), document_uri))    
            relative_graph.add((subj, pred, obj))
        return relative_graph
    
    def to_document_relative_urls(self, absolute_url, document_url):

        # Parse the document URL and get its directory
        document_parsed = urlparse(document_url)
        document_directory = os.path.dirname(document_parsed.path)
        
        abs_parsed = urlparse(absolute_url)

        if not abs_parsed.netloc == document_parsed.netloc:
            return absolute_url
        # Only modify URLs within the same domain
        abs_path = abs_parsed.path
        # Get the relative path from document's directory to the target path
        relative_path = os.path.relpath(abs_path, document_directory)
        
        # Add query and fragment back if they exist
        if abs_parsed.query:
            relative_path += '?' + abs_parsed.query
        if abs_parsed.fragment:
            relative_path += '#' + abs_parsed.fragment
        
        return relative_path
        



    def relurl(self, target, base):
        base = urlparse(base)
        target = urlparse(target)
        if base.netloc != target.netloc:
            raise ValueError('target and base netlocs do not match')
        base_dir = '.' + posixpath.dirname(base.path)
        target = '.' + target.path
        return posixpath.relpath(target,start=base_dir)
    
    # Returns the filename to use for writing, and prepares the directory structure.
    def filepath_for_storage(self, item, spider : Spider):
        adapter = ItemAdapter(item)
        url = adapter.get('url')
        if not url.startswith(spider.base_path):
            # Raise error or drop and log?
            raise ValueError(f"The URL '{url}' does not start with the base path '{spider.base_path}'")
        relative_url = url[len(spider.base_path):]
        relative_url_parts = self.url_parts(relative_url)
        pprint.pprint(relative_url)
        pprint.pprint(relative_url_parts)
        spider.logger.info("Relative : %s", relative_url)
        
        directory_path = spider.fragments_output_dir
        if not directory_path[-1] == '/':
            directory_path += "/"

        append = "/".join(relative_url_parts[0:-1])
        if append:
                directory_path += append + "/"
        spider.logger.info("Storing to : %s", directory_path)
        # Create intermediate directories
        os.makedirs(directory_path, exist_ok=True)
        parsed_url = urlparse(url)
        params = urlunparse(('', '', '', parsed_url.params, parsed_url.query, parsed_url.fragment))
        return directory_path + "/" + relative_url_parts[-1] + urllib.parse.quote_plus(params)

    def url_parts(self, source_url):
        url = unquote(source_url).encode("ascii", "ignore").decode()
        pprint.pprint(url)
        return urlparse(url).path.strip('/').split('/')
