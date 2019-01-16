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
    # pylint: disable=too-many-locals
    matches = nationalities_in_league('Iceland', 'Premier League')
    # matches = nationalities_in_league('Germany', 'Premier League')

    #
    # generate GraphJSON for Alchemy.js visualization JS library
    #
    logging.info('Building GraphJSON...')

    # maps node ID to it's name
    nodes_name_to_id = dict()

    # mapping of matches field to node group, these fields will be a graph node when visualized
    nodes_fields = {
        't.name': 'SportsTeam',
        'p.name': 'Person',
    }

    egde_fields = {
        # athletee relation will connect p.name -> t.name nodes
        'athletee': (
            'p.name', 't.name',
            lambda x: '{}-{}'.format(
                int(float(x['a.since'])),
                int(float(x['a.until'])) if x['a.until'] != 'NULL' else 'now'
            )
        )
    }

    nodes = dict()

    for match in matches:
        for node_field, node_group in nodes_fields.items():
            node_name = '{}:{}'.format(match[node_field], node_group)

            if node_name not in nodes:
                node_id = len(nodes_name_to_id.keys())
                nodes_name_to_id[node_name] = node_id

                logging.info('Adding node #%d: %s', node_id, node_name)

                nodes[node_name] = {
                    'id': node_id,
                    'caption': match[node_field],
                    'type': node_group,
                }

    nodes = list(nodes.values())

    logging.info('Nodes added: %d', len(nodes))

    # now build edges
    edges = []

    for match in matches:
        for edge_type, (from_field, to_field, edge_lambda) in egde_fields.items():
            edge_from = '{}:{}'.format(match[from_field], nodes_fields[from_field])
            edge_to = '{}:{}'.format(match[to_field], nodes_fields[to_field])

            if edge_lambda:
                edge_type = edge_lambda(match)

            logging.info('Adding an edge: %s -> %s (%s)', edge_from, edge_to, edge_type)

            edges.append({
                'source': nodes_name_to_id[edge_from],
                'target': nodes_name_to_id[edge_to],
                'caption': edge_type,
            })

    logging.info('Edges added: %d', len(edges))

    logging.info('Cut here :) ====== ')
    print('\tvar graph = {};'.format(json.dumps({
        'nodes': nodes,
        'edges': edges,
    })))
