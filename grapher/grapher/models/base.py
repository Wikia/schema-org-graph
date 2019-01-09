"""
Base model
"""
import json
import re
from collections import OrderedDict


class BaseModel(object):
    """
    Base schema.org model for keeping metadata
    """
    def __init__(self, model_type, name):
        assert name is not None, 'name of a model cannot be None'

        self.type = model_type
        self.name = name
        self.properties = OrderedDict(name=name)
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

    @staticmethod
    def encode_name(name):
        """
        :type name str
        :rtype: str
        """
        # remove UTF characters
        name = name.encode('ascii', 'ignore').decode('ascii')

        # Must begin with an alphabetic letter
        # Can contain numbers, but not as the first character
        # Cannot contain symbols (an exception to this rule is using underscore)
        #
        # https://neo4j.com/docs/cypher-manual/current/syntax/naming/
        name = re.sub(r'^\d+', '', name)  # remove digits from the beginning of the string
        return re.sub(r'[^a-z0-9]+', '_', name, flags=re.IGNORECASE).strip('_')

    def get_node_name(self):
        """
        Return node name for using in Cypher queries, e.g. "Foo:Type"

        :rtype: str|None
        """
        if self.get_name() is None:
            return None

        return '{}:{}'.format(
            self.encode_name(self.get_name()),
            self.encode_name(self.get_type())
        )

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

    def add_relation(self, relation, target, properties=None):
        """
        :type relation str
        :type target str
        :type properties dict
        """
        # remove None values from properties
        if properties:
            properties = {k: v for k, v in properties.items() if v is not None}

        self.relations.append((relation, target, properties))

    def get_relation_targets(self, relation_type):
        """
        :type relation_type str
        :rtype: list[str]|None
        """
        found = [
            (target, properties) if properties is not None else target
            for (relation, target, properties) in self.relations if relation_type == relation
        ]

        return found if found else None

    def get_all_relations(self):
        """
        :rtype: list[tuple]
        """
        return self.relations

    def __repr__(self):
        ret = '<{} https://schema.org/{} ({}) '.\
            format(self.__class__.__name__, self.get_type(), self.get_node_name())

        # dump node properties
        # (p:Person {name: 'Jennifer'})
        ret += ', '.join([
            '{} = "{}"'.format(key, value)
            for key, value in self.properties.items()
        ])

        ret += '>'

        # dump relations
        # -[rel:IS_FRIENDS_WITH {since: 2018}]->
        for (relation, target, properties) in self.relations:
            ret += '\n\t--[:{} {}]->({})'.format(
                relation, json.dumps(properties or '').strip('" '), target)

        return ret
