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

    template = Template(page_title='The page', name=data['name'], parameters=data['parameters'])
    print(template)

    # simple accessor
    assert template.get_page_title() == 'The page'
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

    assert len(source.get_templates_of_type(template_type='Country flagicon2')) == 17
    assert len(source.get_templates_of_type(template_type='Birth date and age')) == 1

    models = list(source.get_models())
    assert len(models) == 1

    ole = models[0]
    print(ole)

    assert ole.get_node_name() == 'Ole_Gunnar_Solskjr:Person'
    assert ole.get_type() == 'Person'
    assert ole.get_name() == 'Ole Gunnar Solskjær'

    assert ole.get_property('birthDate') == 1973
    assert ole.get_property('birthPlace') == 'Kristiansund'
    assert ole.get_property('nationality') == 'Norway'
    assert ole.get_property('height') == 1.78
    assert ole.get_property('foo') is None

    assert ole.get_relation_targets('athlete') == ['Clausenengen_FK:SportsTeam', 'Molde_FK:SportsTeam', 'Manchester_United_F_C:SportsTeam']
    assert ole.get_relation_targets('coach') == ['Manchester_United_F_C_Reserves_and_Academy:SportsTeam', 'Molde_FK:SportsTeam', 'Cardiff_City_F_C:SportsTeam', 'Molde_FK:SportsTeam', 'Manchester_United_F_C:SportsTeam']

    assert ole.get_relation_targets('foo') is None


def test_allegri():
    fixture = read_fixture('massimiliano_allegri.json')
    source = FootballWikiSource()
    source.set_content(fixture)

    models = list(source.get_models())
    assert len(models) == 1

    coach = models[0]
    print(coach)

    assert coach.get_node_name() == 'Massimiliano_Allegri:Person'
    assert coach.get_type() == 'Person'
    assert coach.get_name() == 'Massimiliano Allegri'

    assert coach.get_property('birthDate') == 1967
    assert coach.get_property('birthPlace') == 'Livorno'
    assert coach.get_property('nationality') == 'Italy'
    assert coach.get_property('height') == 1.83

    assert coach.get_relation_targets('athlete')[-1] == 'Aglianese_Calcio_1923:SportsTeam'
    assert coach.get_relation_targets('coach')[-1] == 'Juventus_F_C:SportsTeam'


def test_zlatan():
    fixture = read_fixture('zlatan.json')
    source = FootballWikiSource()
    source.set_content(fixture)

    models = list(source.get_models())
    assert len(models) == 1

    zlatan = models[0]
    print(zlatan)

    assert zlatan.get_node_name() == 'Zlatan_Ibrahimovi:Person'
    assert zlatan.get_type() == 'Person'
    assert zlatan.get_name() == 'Zlatan Ibrahimović'

    assert zlatan.get_property('birthDate') == 1981
    assert zlatan.get_property('birthPlace') == 'Malmö'
    assert zlatan.get_property('nationality') == 'Sweden'
    assert zlatan.get_property('height') == 1.95

    assert zlatan.get_relation_targets('athlete')[0] == 'Malm_FF:SportsTeam'
    assert zlatan.get_relation_targets('athlete')[-1] == 'LA_Galaxy:SportsTeam'
    assert zlatan.get_relation_targets('coach') is None


def test_manchester_united():
    fixture = read_fixture('manchester_united.json')
    source = FootballWikiSource()
    source.set_content(fixture)

    models = list(source.get_models())
    assert len(models) == 1

    team = models[0]
    print(team)

    assert team.get_node_name() == 'Manchester_United_F_C:SportsTeam'
    assert team.get_type() == 'SportsTeam'
    assert team.get_name() == 'Manchester United F.C.', 'name should be taken from page title to allow proper linking'

    assert team.get_property('sport') == "Football"
    assert team.get_property('foundingDate') == 1878
    assert team.get_property('ground') == 'Old Trafford'
    assert team.get_property('memberOf') == 'Premier League'
    assert team.get_property('url') == 'http://www.manutd.com/'

    assert team.get_relation_targets('coach') == ['Ole_Gunnar_Solskjr:Person']

    assert len(team.get_relation_targets('athlete')) == 29
    assert team.get_relation_targets('athlete')[0] == ('David_de_Gea:Person', {'number': 1, 'position': 'GK'}), 'This relation should have a property'
    assert team.get_relation_targets('athlete')[2] == ('Eric_Bailly:Person', {'number': 3, 'position': 'DF'}), 'This relation should have a property'


def test_burnley():
    fixture = read_fixture('burnley.json')
    source = FootballWikiSource()
    source.set_content(fixture)

    models = list(source.get_models())
    assert len(models) == 1

    team = models[0]
    print(team)

    assert team.get_node_name() == 'Burnley_F_C:SportsTeam'
    assert team.get_type() == 'SportsTeam'
    assert team.get_name() == 'Burnley F.C.', 'name should be taken from page title to allow proper linking'

    assert team.get_relation_targets('coach') == ['Sean_Dyche:Person']

    assert len(team.get_relation_targets('athlete')) == 37
