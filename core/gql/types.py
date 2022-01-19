from graphene import Scalar
from graphql.language import ast
from mongoengine import ObjectIdField


class GrapheneMongoId(Scalar):
    """Graphene representation mongo object id"""

    @staticmethod
    def serialize(id_):
        return str(id_)

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return ObjectIdField().to_mongo(node.value)

    @staticmethod
    def parse_value(value):
        return ObjectIdField().to_mongo(value)
