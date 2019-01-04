from grapher.utils import extract_link, extract_links, extract_year, extract_number


def test_extract_link():
    assert extract_link(' flagiconENG [[Manchester United F.C.|Manchester United]] (caretaker manager) ') == \
        'Manchester United F.C.'

    assert extract_link(' FlagiconNOR [[Norway]] ') == \
        'Norway'

    assert extract_link(' Kristiansund ') is None


def test_extract_links():
    assert extract_links(' FlagiconNOR [[Clausenengen FK|Clausenengen]]<br>FlagiconNOR [[Molde FK|Molde]]<br>FlagiconENG [[Manchester United F.C.|Manchester United]]\n') == \
        ['Clausenengen FK', 'Molde FK', 'Manchester United F.C.']

    assert extract_links(' FlagiconNOR [[Norway]] ') == \
        ['Norway']


def test_extract_year():
    assert extract_year(' Birth date and age19730226df=y ') == '1973'
    assert extract_year(' 19 May 1917 ') == '1917'
    assert extract_year(' 1984 ') == '1984'

    assert extract_year(' 12 july ') is None
    assert extract_year(' 12abcd34 ') is None


def test_extract_number():
    assert extract_number(' Birth date and age19730226df=y ') == 19730226
    assert extract_number(' 19 May 1917 ') == 19
    assert extract_number(' 1984 ') == 1984
    assert extract_number(' 12 july ') == 12
    assert extract_number(' 12abcd34 ') == 12

    assert extract_number(' heightm=1.78 ') == 1.78

    assert extract_year(' abc ') is None
