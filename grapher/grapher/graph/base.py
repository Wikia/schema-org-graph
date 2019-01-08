"""
Base class
"""
import logging


class BaseGraph(object):
    """
    Represents a collection of nodes (model objects) and relations (edges) between them
    """
    def __init__(self):
        self.models = list()
        self.logger = logging.getLogger(self.__class__.__name__)

    def add(self, model):
        """
        :type model grapher.models.BaseModel
        """
        self.models.append(model)

    def store(self, graph_name):
        """
        Save a given graph
        """
        raise NotImplementedError('store methods needs to be implemented')
