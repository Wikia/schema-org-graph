"""
Takes data from Wikia's article
"""
import json
from . import BaseSource
from ..models import PersonModel, SportsTeamModel
from ..utils import extract_year, extract_link, extract_links, extract_number


class Template(object):
    """
    Accessor for parameters of template
    """
    def __init__(self, page_title, name, parameters):
        """
        :type page_title str
        :type name str
        :type parameters dict
        """
        self.page_title = page_title
        self.name = name
        self.parameters = parameters

    def get_page_title(self):
        """
        :rtype: str
        """
        return self.page_title

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
        page_title = self.get_content_json()['title']

        for template in self.get_content_json().get('templates'):
            yield Template(
                page_title=page_title,
                name=template['name'],
                parameters=template['parameters']
            )

    def get_models(self):
        super(WikiArticleSource, self).get_models()


class FootballWikiSource(WikiArticleSource):
    """
    Takes metadata from football.wikia.com
    """
    def get_models(self):
        for template in self.get_templates():
            if template.get_name() == 'Infobox Biography':
                # https://schema.org/Person
                # print(template)

                model = PersonModel(name=template['fullname'])

                model.add_property('birthDate', template.get_year('dateofbirth'))
                model.add_property('birthPlace', template['cityofbirth'])
                model.add_property('nationality', template.get_link('countryofbirth'))
                model.add_property('height', template.get_number('height'))  # [m]

                # add relations
                for club_name in template.get_links('clubs') or []:
                    model.add_relation('athlete', SportsTeamModel(club_name).get_node_name())

                for club_name in template.get_links('managerclubs') or []:
                    model.add_relation('coach', SportsTeamModel(club_name).get_node_name())

                yield model

            elif template.get_name() == 'Infobox Club':
                # https://schema.org/SportsTeam
                # print(template)

                model = SportsTeamModel(name=template.get_page_title())
                model.add_property('sport', 'Football')

                model.add_property('foundingDate', template.get_year('founded'))
                model.add_property('ground', template.get_link('ground'))
                model.add_property('memberOf', template.get_link('lastleague'))
                model.add_property('nationality', template.get_link('countryofbirth'))
                model.add_property('url', template['website'])

                model.add_relation('coach', PersonModel(
                    name=template.get_link('manager')).get_node_name())

                # now, let's try to extract all players in the current squad
                players_templates = [
                    template
                    for template in self.get_templates() if template.get_name() == 'Fs player'
                ]

                for player in players_templates:
                    # name is not always a link
                    player_name = player.get_link('name') or player['name']

                    if player_name:
                        model.add_relation(
                            'athlete',
                            PersonModel(player_name).get_node_name(),
                            {'position': player['pos']}
                        )
                    else:
                        self.logger.error('%s returned an empty player name (for %s)',
                                          player, model.get_node_name())

                yield model
