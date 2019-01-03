from os import path

from grapher.sources import FootballWikiSource


def read_fixture(fixture_name):
    """
    :rtype: str
    """
    directory = path.dirname(__file__)

    with open(path.join(directory, 'fixtures', fixture_name), 'rt') as fixture:
        return fixture.read()


def test_ole_gunnar():
    fixture = read_fixture('ole_gunnar.json')
    source = FootballWikiSource()
    source.set_content(fixture)

    models = source.get_models()

    print(list(models))
    assert False
