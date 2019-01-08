"""
This script takes data from football.wikia.com and loads into RedisGraph database
"""
import logging
from hashlib import md5
from os import path

import redis
import requests

# from data_flow_graph import format_graphviz_lines
from mwclient.client import Site
from grapher.sources.wiki import WikiArticleSource, FootballWikiSource

# for RedisGraph
from redisgraph import Node, Edge, Graph

# where graphs will be stored
OUTPUT_DIRECTORY = path.join(path.dirname(__file__), '../../output/')

# http://football.sandbox-s6.wikia.com/api/v1/Templates/Metadata?title=Zlatan_Ibrahimovi%C4%87
WIKI_DOMAIN = 'football.sandbox-s6.wikia.com'

# for start index pages from these categories only
CATEGORIES = [
    'Premier_League_clubs',
    'Premier_League_players',
    'Premier_League_managers',

    # 'Serie_A_clubs',
    # 'Italian_players',
    # Italian_Coaches',
]


class Wiki(object):
    """
    A simple wrapper for mwclient library
    """
    def __init__(self, wiki):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('Using %s wiki', wiki)

        self.pool = requests.Session()
        self.pool.proxies = {'http': 'border-http-s3:80'}
        self.site = Site(host=('http', wiki), path='/', pool=self.pool)

        self.cache_dir = path.join(path.dirname(__file__), '.cache')
        self.logger.info("Using cache directory: %s", self.cache_dir)

    def _get_cache_filename(self, entry_type, name):
        """
        Return a hashed filename of cache entry for a given URL
        :type entry_type str
        :type name str
        :rtype: str
        """
        _hash = md5()
        _hash.update(name.encode('utf-8'))

        return path.join(
            self.cache_dir,
            '{}_{}.json'.format(entry_type, _hash.hexdigest())
        )

    def pages_in_category(self, category_name):
        """
        :type category_name str
        :rtype: list[str]
        """
        self.logger.info('Getting pages in "%s" category', category_name)

        category = self.site.categories[category_name]
        count = 0
        for page in category:
            # only NS_MAIN pages
            if page.namespace == 0:
                count += 1
                yield page.name

        self.logger.info('Returned %d pages', count)

    def get_models_from_page(self, title, source=WikiArticleSource()):
        """
        :type title str
        :type source WikiArticleSource
        :rtype: list[grapher.models.base.BaseModel]
        """
        self.logger.info('Getting metadata for "%s"', title)

        # https://nfs.sandbox-s6.fandom.com/wikia.php?controller=TemplatesApiController&method=getMetadata&title=Ferrari_355_F1
        # http://football.sandbox-s6.wikia.com/api/v1/Templates/Metadata?title=Zlatan_Ibrahimovi%C4%87
        # http://football.sandbox-s6.wikia.com/api/v1/Templates/Metadata?title=Zlatan_Ibrahimovi%C4%87
        cache_file = self._get_cache_filename('templates', title)

        if not path.isfile(cache_file):
            res_raw = self.pool.get(
                'http://football.sandbox-s6.wikia.com/api/v1/Templates/Metadata',
                params={'title': title}
            ).text

            # set the cache
            with open(cache_file, 'wt') as file:
                file.write(res_raw)
        else:
            # cache hit
            with open(cache_file, 'rt') as file:
                res_raw = file.read()

        source.set_content(res_raw)

        return source.get_models()


class BaseGraph(object):
    """
    Represents a collection of nodes (model objects) and relations (edges) between them
    """
    def __init__(self):
        self.models = list()
        self.logger = logging.getLogger(self.__class__.__name__)

    def add(self, model):
        """
        :type model grapher.models.BaseModel
        """
        self.models.append(model)

    def store(self, graph_name):
        """
        Save a given graph
        """
        raise NotImplementedError('store methods needs to be implemented')


class RedisGraph(BaseGraph):
    """
    Handles storing a collection of models in RedisGraph
    """
    def __init__(self, host, port=6379):
        """
        :type host str
        :type port int
        """
        super(RedisGraph, self).__init__()

        self.host = host
        self.port = port

        self.logger.info('Using redis: %s:%d', host, port)

    @staticmethod
    def model_to_node(model):
        """
        :type model grapher.models.BaseModel
        :rtype: Node
        """
        properties = dict(name=model.get_name())
        properties.update(model.properties)

        return Node(
            alias=model.get_node_name(),
            properties=properties,
        )

    @staticmethod
    def model_to_edges(model):
        """
        :type model grapher.models.BaseModel
        :rtype: list[Edge]
        """
        for (relation, target, properties) in model.get_all_relations():
            # Edge(john, 'visited', japan, properties={'purpose': 'pleasure'})
            yield Edge(
                src_node=Node(alias=model.get_node_name()),
                relation=relation,
                dest_node=Node(alias=target),
                properties=properties
            )

    def store(self, graph_name):
        """
        :type graph_name str
        """
        # https://github.com/RedisLabs/redisgraph-py#example-using-the-python-client
        redis_graph = Graph(
            name=graph_name,
            redis_con=redis.Redis(self.host, self.port)
        )

        # add all nodes
        for model in self.models:
            redis_graph.add_node(self.model_to_node(model))

        # and now add edges
        for model in self.models:
            for edge in self.model_to_edges(model):
                try:
                    # add target node if needed
                    # we may want to refer to a node that was not indexed above
                    # e.g. English player in a Spanish club
                    if edge.dest_node.alias not in redis_graph.nodes:
                        redis_graph.add_node(Node(alias=edge.dest_node.alias))

                    redis_graph.add_edge(edge)
                except KeyError:
                    print(model)
                    # graph can be not complete, some nodes can be missing despite the relation
                    self.logger.error('add_edge failed', exc_info=True)

        # and save it
        self.logger.info('Committing graph with %d nodes and %s edges',
                         len(redis_graph.nodes), len(redis_graph.edges))

        redis_graph.commit()
        redis_graph.redis_con.execute_command('SAvE')

        self.logger.info('Committed and saved')


def index():
    """
    Index football.wikia.com
    """
    logger = logging.getLogger('index')
    logger.info('Script: %s', __file__)
    logger.info('Output: %s', OUTPUT_DIRECTORY)

    wiki = Wiki(WIKI_DOMAIN)

    # get pages in categories we're interested in
    pages = []
    for category in CATEGORIES:
        pages += wiki.pages_in_category(category)

    # make the list unique (we may have the same page in players and manager category)
    # and sort it
    pages = sorted(list(set(pages)))

    # get and parse templates
    logger.info("Will create models from %d pages", len(pages))

    models = []
    for page in pages:
        models += wiki.get_models_from_page(page, source=FootballWikiSource())

    logger.info("%d models were created from pages", len(models))
    # print([model.get_node_name() for model in models])

    # store graph in RedisGraph
    graph = RedisGraph(host='localhost', port=56379)
    for model in models:
        graph.add(model)

    graph.store('football')

    """
    # ok, now generate dot file
    lines = []

    for model in models:
        # render each relation as an edge in dot file (graphviz format)
        # https://github.com/macbre/data-flow-graph
        for (relation, target, _) in model.get_all_relations():
            lines.append({
                'source': model.get_node_name(),
                'metadata': relation,
                'target': target
            })

    logger.info("Saving %d edges to dot file", len(lines))

    with open(OUTPUT_DIRECTORY + '/football.dot', 'wt') as dot_file:
        dot_file.writelines(format_graphviz_lines(lines))

    logger.info('Done')
    """
