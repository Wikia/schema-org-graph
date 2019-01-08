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
    def model_to_node(model):
        """
        :type model grapher.models.BaseModel
        :rtype: Node
        """
        properties = dict(name=model.get_name())
        properties.update(model.properties)

        return Node(
            alias=model.get_node_name(),
            properties=properties,
        )

    @staticmethod
    def model_to_edges(model):
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
                properties=properties
            )

    def store(self, graph_name):
        """
        :type graph_name str
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
                        redis_graph.add_node(Node(alias=edge.dest_node.alias))
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

        # and save it
        self.logger.info('Committing graph with %d nodes and %s edges',
                         len(redis_graph.nodes), len(redis_graph.edges))

        redis_graph.commit()
        redis_graph.redis_con.execute_command('SAvE')

        self.logger.info('Committed and saved')
