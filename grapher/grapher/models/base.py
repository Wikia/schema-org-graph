"""
Base model
"""
from collections import OrderedDict


class BaseModel(object):
    """
    Base schema.org model for keeping metadata
    """
    def __init__(self, model_type, name):
        self.type = model_type
        self.name = name
        self.properties = OrderedDict()
        self.relations = list()

    def get_type(self):
        """
        :rtype: str
        """
        return self.type

    def get_name(self):
        """
        :rtype: str
        """
        return self.name

    def add_property(self, key, value):
        """
        :type key str
        :type value str|int|float
        """
        if value is not None:
            self.properties[key] = value

    def get_property(self, key):
        """
        :type key str
        :rtype: str|int|float|None
        """
        return self.properties.get(key)

    def add_relation(self, relation, target):
        """
        :type relation str
        :type target str
        """
        self.relations.append((relation, target))

    def get_relation_targets(self, relation_type):
        """
        :type relation_type str
        :rtype: list[str]|None
        """
        found = [
            target
            for (relation, target) in self.relations if relation_type == relation
        ]

        return found if found else None

    def __repr__(self):
        ret = '<{} https://schema.org/{} "{}" '.\
            format(self.__class__.__name__, self.get_type(), self.get_name())

        # dump properties
        ret += ', '.join([
            '{} = "{}"'.format(key, value)
            for key, value in self.properties.items()
        ])

        ret += '>'

        # dump relations
        for (relation, target) in self.relations:
            ret += '\n\t--> {} --> {}'.format(relation, target).rstrip()

        return ret
