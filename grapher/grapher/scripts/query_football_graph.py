"""
Ask a question for a football graph
"""
# https://wikia-inc.atlassian.net/browse/CORE-28
import json
import logging

from grapher.graph import RedisGraph


def query_redis(graph_name, query, **params):
    """
    :type graph_name str
    :type query str
    :rtype: list[dict]
    """
    cypher_query = query.format(**params).rstrip()

    logging.info('Querying "%s" graph: %s', graph_name, cypher_query)
    graph = RedisGraph(host='localhost', port=56379).get_redisgraph(graph_name)
    res = graph.query(cypher_query)

    # res.pretty_print()  # DEBUG

    results = res.result_set
    header = [str(entry.decode("utf-8")) for entry in results[0]]

    for row in results[1:]:
        yield dict(
            zip(header, [str(entry.decode("utf-8")) for entry in row])
        )


def nationalities_in_league(nationality, league):
    """
    :type nationality str
    :type league str
    :rtype: list[dict]
    """
    logging.info('Looking for players from %s in %s', nationality, league)

    query = """
    MATCH (t:SportsTeam)<-[a:athlete]-(p:Person)
    WHERE t.memberOf = '{league}'
    AND p.nationality = '{nationality}' RETURN t.name,p.name,a.since,a.until
    """

    matches = query_redis('football', query, nationality=nationality, league=league)
    matches = list(matches)

    print("\n".join([str(match) for match in matches]))

    return matches


def index():
    """
    Script's entry point
    """
    # nationalities_in_league('Iceland', 'Premier League')
    matches = nationalities_in_league('Germany', 'Premier League')

    #
    # generate a graph for visjs library
    #
    logging.info('Building a graph data for visjs')

    # mapping of matches field to node group, these fields will be a graph node when visualized
    # http://visjs.org/docs/network/nodes.html
    nodes_fields = {
        't.name': 'SportsTeam',
        'p.name': 'Person',
    }

    # http://visjs.org/docs/network/edges.html
    egde_fields = {
        'athletee': ('p.name', 't.name')  # athletee relation will connect p.name -> t.name nodes
    }

    nodes = dict()

    for match in matches:
        for node_field, node_group in nodes_fields.items():
            node_id = '{}:{}'.format(match[node_field], node_group)

            if node_id not in nodes:
                logging.info('Adding a node: %s', node_id)

                nodes[node_id] = {
                    'id': node_id,
                    'label': match[node_field],
                    'group': node_group,
                }

    nodes = list(nodes.values())

    logging.info('Nodes added: %d', len(nodes))

    # now build edges
    edges = []

    for match in matches:
        for edge_type, (from_field, to_field) in egde_fields.items():
            edge_from = '{}:{}'.format(match[from_field], nodes_fields[from_field])
            edge_to = '{}:{}'.format(match[to_field], nodes_fields[to_field])

            logging.info('Adding an edge: %s -> %s', edge_from, edge_to)

            edges.append({
                'from': edge_from,
                'to': edge_to,
                'label': edge_type,
                'arrows': 'to',
            })

    logging.info('Edges added: %d', len(edges))

    logging.info('Cut here :) ====== ')
    print('var data = ' + json.dumps({
        'nodes': nodes,
        'edges': edges,
    }))
