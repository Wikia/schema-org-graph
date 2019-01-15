"""
Ask a question for a football graph
"""
# https://wikia-inc.atlassian.net/browse/CORE-28
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
    """
    logging.info('Looking for players from %s in %s', nationality, league)

    query = """
    MATCH (t:SportsTeam)<-[a:athlete]-(p:Person)
    WHERE t.memberOf = '{league}'
    AND p.nationality = '{nationality}' RETURN t.name,p.name,a.since,a.until
    """

    matches = query_redis('football', query, nationality=nationality, league=league)

    print("\n".join([str(match) for match in matches]))


def index():
    """
    Script's entry point
    """
    nationalities_in_league('Iceland', 'Premier League')
