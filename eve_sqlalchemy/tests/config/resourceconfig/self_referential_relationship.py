# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from eve_sqlalchemy.config import ResourceConfig

from .. import BaseModel
from . import ResourceConfigTestCase

Base = declarative_base(cls=BaseModel)


class Node(Base):
    name = Column(String(16), primary_key=True)
    parent_node_name = Column(String(16), ForeignKey('node.name'))
    parent_node = relationship("Node", remote_side=[name])


class TestSelfReferentialRelationship(ResourceConfigTestCase):

    def setUp(self):
        super(TestSelfReferentialRelationship, self).setUp()
        self._related_resource_configs = {
            Node: ('nodes', ResourceConfig(Node))
        }

    def test_node_projection(self):
        projection = self._render(Node)['datasource']['projection']
        self.assertEqual(projection, {'_etag': 0, 'name': 1, 'parent_node': 1})

    def test_node_schema(self):
        schema = self._render(Node)['schema']
        self.assertIn('parent_node', schema)
        self.assertNotIn('parent_node_name', schema)
        self.assertEqual(schema['parent_node'], {
            'type': 'string',
            'data_relation': {
                'resource': 'nodes',
                'field': 'name'
            },
            'local_id_field': 'parent_node_name',
            'nullable': True
        })
