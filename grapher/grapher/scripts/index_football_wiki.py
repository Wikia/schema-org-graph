"""
This script takes data from football.wikia.com and loads into RedisGraph database
"""
import json
import logging

import requests
from mwclient.client import Site
from grapher.sources.wiki import WikiArticleSource, FootballWikiSource

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
    logger = logging.getLogger('index')
    logger.info('Running %s', __file__)

    wiki = Wiki(WIKI_DOMAIN)

    # get pages in categories we're interested in
    pages = []
    for category in CATEGORIES:
        pages += list(wiki.pages_in_category(category))

    # get and parse templates
    logger.info("Will index %d pages", len(pages))

    models = []
    for page in pages[:10]:
        models += wiki.get_models_from_page(page, source=FootballWikiSource())

    print(models)

    logger.info("%d models were index", len(models))
    logger.info('Done')
