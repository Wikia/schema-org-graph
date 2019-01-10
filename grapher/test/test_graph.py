from grapher.models import PersonModel
from grapher.graph import RedisGraph


def test_dump():
    graph = RedisGraph(host='foo')

    graham = PersonModel(
        name='Graham Chapman',
    )

    john = PersonModel(
        name='John Cleese',
    )
    john.add_relation('plays_with', graham.get_node_name())

    graph.add(model=graham)
    graph.add(model=john)

    dump = graph.dump('circus')
    print(dump)

    assert 'GRAPH.QUERY circus "CREATE' in dump
    assert '(Graham_Chapman:Person{name:\\"Graham Chapman\\"})' in dump
    assert '(John_Cleese:Person{name:\\"John Cleese\\"})' in dump
    assert '(John_Cleese:Person)-[:plays_with]->(Graham_Chapman:Person)' in dump
