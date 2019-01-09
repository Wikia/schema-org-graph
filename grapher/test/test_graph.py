from grapher.models import PersonModel
from grapher.graph import RedisGraph


def test_dump():
    graph = RedisGraph(host='foo')
    person = PersonModel(
        name='Monty Python'
    )

    graph.add(model=person)

    assert graph.dump('circus') == 'GRAPH.QUERY circus "CREATE (Monty_Python:Person{name:\\"Monty Python\\"})"'
