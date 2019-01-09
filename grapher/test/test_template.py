from grapher.sources.wiki import Template


def test_tenplate_params():
    template = Template(
        page_title='The page',
        name='Foo',
        parameters={
            'foo': '',
            'bar': '  ',
            'link': '123 [[abc]] 456',
            'number': '42.5 m'
        }
    )
    print(template)

    assert template.get_page_title() == 'The page'
    assert template.get_name() == 'Foo'
    assert template['foo'] is None, 'Empty string should be treated as no value at all'
    assert template['bar'] is None, 'Spaces should be treated as no value at all'
    assert template.get_link('link') == 'abc'
    assert template.get_number('number') == 42.5
