from grapher.sources import FootballWikiSource
from grapher.sources.wiki import Template


def test_extract_clubs_and_years():
    template = Template(
        page_title='Foo',
        name='Bar',
        parameters={
            'years': " 1990–1994<br>1994–1996<br>1996–2007<br>'''Total''' ",
            'clubs': " FlagiconNOR [[Clausenengen FK|Clausenengen]]<br>FlagiconNOR [[Molde FK|Molde]]<br>FlagiconENG [[Manchester United F.C.|Manchester United]] ",
        }
    )

    relations = list(FootballWikiSource.extract_clubs_and_years(template, 'clubs', 'years'))
    print(relations)

    assert len(relations) == 3
    assert relations[0] == ('Clausenengen FK', (1990, 1994))
    assert relations[1] == ('Molde FK', (1994, 1996))
    assert relations[2] == ('Manchester United F.C.', (1996, 2007))


def test_extract_clubs_and_years_open_period():
    template = Template(
        page_title='Foo',
        name='Bar',
        parameters={
            'years': " 2011-2012<br>2012-2016<br>2016–2018<br>2017–2018<br>2018- ",
            'clubs': " flagiconITA [[A.C. Milan|Milan]]<br>flagiconFRA [[Paris Saint-Germain F.C.|Paris Saint-Germain]]<br>flagiconENG [[Manchester United]]<br>flagiconENG [[Manchester United]]<br>flagiconUSA [[LA Galaxy] ",
        }
    )

    relations = list(FootballWikiSource.extract_clubs_and_years(template, 'clubs', 'years'))
    print(relations)

    assert len(relations) == 5
    assert relations[0] == ('A.C. Milan', (2011, 2012))
    assert relations[1] == ('Paris Saint-Germain F.C.', (2012, 2016))
    assert relations[2] == ('Manchester United', (2016, 2018))
    assert relations[3] == ('Manchester United', (2017, 2018))
    assert relations[4] == ('LA Galaxy', (2018, None)), 'Properly parses and open period'
