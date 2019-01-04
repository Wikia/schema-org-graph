import json
from os import path

from grapher.sources import FootballWikiSource
from grapher.sources.wiki import Template


def read_fixture(fixture_name):
    """
    :rtype: str
    """
    directory = path.dirname(__file__)

    with open(path.join(directory, 'fixtures', fixture_name), 'rt') as fixture:
        return fixture.read()


def test_template():
    fixture = read_fixture('ole_gunnar.json')
    data = json.loads(fixture)['templates'][0]

    template = Template(name=data['name'], parameters=data['parameters'])
    print(template)

    # simple accessor
    assert template.get_name() == 'Infobox Biography'
    assert template['cityofbirth'] == 'Kristiansund', 'Parameter value should be trimmed'
    assert template['clubnumber'] == '', 'Empty parameter should return an empty string'
    assert template['foo'] is None, 'Not defined parameter should return None'

    # values extraction
    assert template.get_year('dateofbirth') == 1973
    assert template.get_year('cityofbirth') is None
    assert template.get_year('foo') is None

    assert template.get_number('dateofbirth') == 19730226
    assert template.get_number('height') == 1.78
    assert template.get_number('cityofbirth') is None
    assert template.get_number('foo') is None

    assert template.get_link('currentclub') == 'Manchester United F.C.'
    assert template.get_link('foo') is None

    assert template.get_links('clubs') == ['Clausenengen FK', 'Molde FK', 'Manchester United F.C.']
    assert template.get_links('currentclub') == ['Manchester United F.C.']
    assert template.get_links('foo') == []


def test_ole_gunnar():
    fixture = read_fixture('ole_gunnar.json')
    source = FootballWikiSource()
    source.set_content(fixture)

    models = list(source.get_models())
    assert len(models) == 1

    ole = models[0]
    print(ole)

    assert ole.get_type() == 'Person'
    assert ole.get_name() == 'Ole Gunnar Solskjær'

    assert ole.get_property('birthDate') == 1973
    assert ole.get_property('birthPlace') == 'Kristiansund'
    assert ole.get_property('nationality') == 'Norway'
    assert ole.get_property('height') == 1.78
    assert ole.get_property('foo') is None

    assert ole.get_relation_targets('athlete') == ['Clausenengen FK', 'Molde FK', 'Manchester United F.C.']
    assert ole.get_relation_targets('coach') == ['Manchester United F.C. Reserves and Academy', 'Molde FK', 'Cardiff City F.C.', 'Molde FK', 'Manchester United F.C.']

    assert ole.get_relation_targets('foo') is None
