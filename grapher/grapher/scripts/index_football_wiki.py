"""
This script takes data from football.wikia.com and loads into RedisGraph database
"""
import logging
from os import path

import requests
from data_flow_graph import format_graphviz_lines
from mwclient.client import Site
from grapher.sources.wiki import WikiArticleSource, FootballWikiSource

# where graphs will be stored
OUTPUT_DIRECTORY = path.join(path.dirname(__file__), '../../output/')

# http://football.sandbox-s6.wikia.com/api/v1/Templates/Metadata?title=Zlatan_Ibrahimovi%C4%87
WIKI_DOMAIN = 'football.sandbox-s6.wikia.com'

# for start index pages from these categories only
CATEGORIES = [
    'Premier_League_clubs',
    'Premier_League_players',
    'Premier_League_managers',

    'Serie_A_clubs',
    'Italian_players',
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
        self.pool.proxies = {'http': 'border-http-s3:80'}
        self.site = Site(host=('http', wiki), path='/', pool=self.pool)

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
        res_raw = self.pool.get(
            'http://football.sandbox-s6.wikia.com/api/v1/Templates/Metadata',
            params={'title': title}
        )

        source.set_content(res_raw.text)

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

    # get and parse templates
    logger.info("Will create models from %d pages", len(pages))

    models = []
    for page in pages:
        models += wiki.get_models_from_page(page, source=FootballWikiSource())

    logger.info("%d models were created from pages", len(models))
    # print([model.get_node_name() for model in models])

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