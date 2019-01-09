"""
Redis storage
"""
import redis
from redisgraph import Node, Edge, Graph
from .base import BaseGraph


class RedisGraph(BaseGraph):
    """
    Handles storing a collection of models in RedisGraph
    """
    def __init__(self, host, port=6379):
        """
        :type host str
        :type port int
        """
        super(RedisGraph, self).__init__()

        self.host = host
        self.port = port

        self.logger.info('Using redis: %s:%d', host, port)

    @staticmethod
    def encode_properties(properties):
        """
        :type properties dict
        :rtype: dict
        """
        ret = dict()

        # redisgraph library does not encode quotes
        # (John_Faxe_Jensen:Person{name:\"John \"Faxe\" Jensen\",birthDate:1965,height:1.78})
        for key, value in properties.items():
            ret[key] = value.replace('"', '\\"') if isinstance(value, str) else value

        return ret

    @classmethod
    def model_to_node(cls, model):
        """
        :type model grapher.models.BaseModel
        :rtype: Node
        """
        properties = dict(name=model.get_name())
        properties.update(model.properties)

        return Node(
            alias=model.get_node_name(),
            properties=cls.encode_properties(properties) if properties else None,
        )

    @classmethod
    def model_to_edges(cls, model):
        """
        :type model grapher.models.BaseModel
        :rtype: list[Edge]
        """
        for (relation, target, properties) in model.get_all_relations():
            # Edge(john, 'visited', japan, properties={'purpose': 'pleasure'})
            yield Edge(
                src_node=Node(alias=model.get_node_name()),
                relation=relation,
                dest_node=Node(alias=target),
                properties=cls.encode_properties(properties) if properties else None
            )

    def _get_graph(self, graph_name):
        """
        :type graph_name str
        :rtype: Graph
        """
        # https://github.com/RedisLabs/redisgraph-py#example-using-the-python-client
        redis_graph = Graph(
            name=graph_name,
            redis_con=redis.Redis(self.host, self.port)
        )

        # add all nodes
        for model in self.models:
            redis_graph.add_node(self.model_to_node(model))

        # and now add edges
        for model in self.models:
            for edge in self.model_to_edges(model):
                try:
                    # add target node if needed
                    # we may want to refer to a node that was not indexed above
                    # e.g. English player in a Spanish club
                    if edge.dest_node.alias not in redis_graph.nodes:
                        node = Node(
                            alias=edge.dest_node.alias,
                            properties={'name': str(edge.dest_node.alias).split(':')[0]}
                        )
                        redis_graph.add_node(node)
                        self.logger.info('Adding missing node: %s', edge.dest_node.alias)

                    redis_graph.add_edge(edge)
                except KeyError:
                    print(model)
                    # graph can be not complete, some nodes can be missing despite the relation
                    self.logger.error('add_edge failed', exc_info=True)

        # assert valid nodes
        # for _, node in redis_graph.nodes.items():
        #    print(node.alias, node.properties)
        #    print(str(node))
        return redis_graph

    def dump(self, graph_name):
        """
        Return a redisgraph command that would create a graph

        :type graph_name str
        :rtype: str
        """
        redis_graph = self._get_graph(graph_name)

        # https://oss.redislabs.com/redisgraph/#with-redis-cli
        # copied from redisgraph/client.py (commit function)
        query = ''

        for _, node in redis_graph.nodes.items():
            query += str(node) + ','

        for edge in redis_graph.edges:
            query += str(edge) + ','

        # Discard leading comma.
        if query[-1] is ',':
            query = query[:-1]

        # encode "
        query = query.replace('"', '\\"')

        return 'GRAPH.QUERY {name} "CREATE {graph}"'.format(name=graph_name, graph=query)

    def store(self, graph_name):
        """
        Store the graph in Redis

        :type graph_name str
        """
        redis_graph = self._get_graph(graph_name)

        # and save it
        self.logger.info('Committing graph with %d nodes and %s edges',
                         len(redis_graph.nodes), len(redis_graph.edges))

        try:
            redis_graph.delete()
        except redis.exceptions.ResponseError as ex:
            # Graph was not found in database.
            self.logger.info(ex)

        redis_graph.commit()

        redis_graph.redis_con.execute_command('SAvE')
        self.logger.info('Committed and saved')
