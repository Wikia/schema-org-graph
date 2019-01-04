"""
Base model
"""
from collections import OrderedDict


class BaseModel(object):
    def __init__(self, model_type, name):
        self.type = model_type
        self.name = name
        self.properties = OrderedDict()
        self.relations = list()

    def add_property(self, key, value):
        self.properties[key] = value

    def add_relation(self, key, target):
        self.relations.append((key, target))

    def __repr__(self):
        ret = '<{} https://schema.org/{} {}>'.format(self.__class__.__name__, self.type, self.name)

        for key, value in self.properties.items():
            ret += '\n\t{}: {}'.format(key, value).rstrip()

        for (relation, target) in self.relations:
            ret += '\n\t--> {} --> {}'.format(relation, target).rstrip()

        return ret
