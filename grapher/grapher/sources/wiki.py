"""
Takes data from Wikia's article
"""
import json
from . import BaseSource
from ..models import PersonModel
from ..utils import extract_year, extract_link, extract_links, extract_number


class Template(object):
    """
    Accessor for parameters of template
    """
    def __init__(self, name, parameters):
        """
        :type name str
        :type parameters dict
        """
        self.name = name
        self.parameters = parameters

    def get_name(self):
        """
        :rtype: str
        """
        return self.name

    def get_year(self, item):
        """
        :rtype: int|None
        """
        return extract_year(self[item]) if self[item] else None

    def get_number(self, item):
        """
        :rtype: int|float|None
        """
        return extract_number(self[item]) if self[item] else None

    def get_link(self, item):
        """
        :rtype: str|None
        """
        return extract_link(self[item]) if self[item] else None

    def get_links(self, item):
        """
        :rtype: list[str]
        """
        return extract_links(self[item]) if self[item] else []

    def __getitem__(self, item):
        """
        :rtype: str|int|float|None
        """
        value = self.parameters.get(item)

        # remove trailing whitespaces from string values
        if isinstance(value, str):
            return value.strip()

        return value

    def __repr__(self):
        return '<Template {} {}>'.format(
            self.name, json.dumps(self.parameters, indent=True, sort_keys=True))


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
        :rtype: list[Template]
        """
        for template in self.get_content_json().get('templates'):
            yield Template(name=template['name'], parameters=template['parameters'])

    def get_models(self):
        super(WikiArticleSource, self).get_models()


class FootballWikiSource(WikiArticleSource):
    """
    Takes metadata from football.wikia.com
    """
    def get_models(self):
        for template in self.get_templates():
            if template.get_name() == 'Infobox Biography':
                print(template)

                model = PersonModel(name=template_parameters['fullname'])

                model.add_property('birthDate', extract_year(template_parameters['dateofbirth']))
                model.add_property('birthPlace', template_parameters['cityofbirth'])
                model.add_property('nationality',
                                   extract_link(template_parameters['countryofbirth']))
                model.add_property('height', extract_number(template_parameters['height']))  # [m]

                # add relations
                for club in extract_links(template_parameters['clubs']):
                    model.add_relation('athlete', club)

                for club in extract_links(template_parameters['managerclubs']):
                    model.add_relation('coach', club)

                # return it
                yield model
