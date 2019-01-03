"""
Takes data from Wikia's article
"""
import json
from . import BaseSource
from ..models import PersonModel
from ..utils import extract_year, extract_link, extract_links


class WikiArticleSource(BaseSource):
    """
    All wiki-specific sources should inherit from this class
    """
    def __init__(self):
        super(WikiArticleSource, self).__init__()
        self.content = None

    def set_content(self, content):
        """
        :type content str
        """
        self.content = content

    def get_content(self):
        """
        :rtype: str
        """
        if not self.content:
            # TODO: fetch content
            pass

        return self.content

    def get_content_json(self):
        """
        :rtype: dict
        """
        return json.loads(self.get_content())

    def get_templates(self):
        """
        :rtype: list[dict]
        """
        for template in self.get_content_json().get('templates'):
            yield template


class FootballWikiSource(WikiArticleSource):
    """
    Takes metadata from football.wikia.com
    """
    def get_models(self):
        for template in self.get_templates():
            template_name = template['name']
            template_parameters = template['parameters']

            if template_name == 'Infobox Biography':
                print(json.dumps(template_parameters, indent=True, sort_keys=True))

                model = PersonModel(
                    name=template_parameters['fullname'],
                    birth_date=extract_year(template_parameters['dateofbirth'])
                )

                # add relations
                for club in extract_links(template_parameters['clubs']):
                    model.add_relation('athlete', club)

                for club in extract_links(template_parameters['managerclubs']):
                    model.add_relation('coach', club)

                # return it
                yield model
