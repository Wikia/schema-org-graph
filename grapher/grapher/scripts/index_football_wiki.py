"""
This script takes data from football.wikia.com and loads into RedisGraph database
"""
import logging
from hashlib import md5
from os import path

import requests

from mwclient.client import Site
from grapher.sources.wiki import WikiArticleSource, FootballWikiSource
from grapher.graph import RedisGraph

# where graphs will be stored
OUTPUT_DIRECTORY = path.join(path.dirname(__file__), '../../output/')

# http://football.sandbox-s6.wikia.com/api/v1/Templates/Metadata?title=Zlatan_Ibrahimovi%C4%87
WIKI_DOMAIN = 'football.wikia.com'

CATEGORIES = [
    'Players',

    # for start index Premier League and Serie A only
    'Premier_League_clubs',
    'Premier_League_managers',

    'Serie_A_clubs',
    'Italian_Coaches',
]


class Wiki(object):
    """
    A simple wrapper for mwclient library
    """
    def __init__(self, wiki):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('Using %s wiki', wiki)

        self.pool = requests.Session()
        # self.pool.proxies = {'http': 'border-http-s3:80'}
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

    # store the graph in a file
    with open(OUTPUT_DIRECTORY + '/football.graph', 'wt') as graph_file:
        graph_file.write(graph.dump(graph_name='football'))

    # save it in a storage
    graph.store(graph_name='football')

    logger.info('Done')
