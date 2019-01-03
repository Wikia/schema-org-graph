"""
Base source class
"""
import logging

from ..models.base import BaseModel


class BaseSource(object):
    """
    All sources should inherit from this class
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_models(self):
        """
        :rtype: list[BaseModel]
        """
        raise NotImplementedError("%s.get_models() needs to be implemented" % self.__class__.__name__)
