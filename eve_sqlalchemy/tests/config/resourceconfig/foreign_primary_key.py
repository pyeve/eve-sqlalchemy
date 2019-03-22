# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from eve_sqlalchemy.config import ResourceConfig

from .. import BaseModel
from . import ResourceConfigTestCase

Base = declarative_base(cls=BaseModel)


class Node(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)


class Lock(Base):
    node_id = Column(Integer, ForeignKey('node.id'),
                     primary_key=True, nullable=False)
    node = relationship('Node', uselist=False, backref='lock')


class TestForeignPrimaryKey(ResourceConfigTestCase):

    def setUp(self):
        super(TestForeignPrimaryKey, self).setUp()
        self._related_resource_configs = {
            Node: ('nodes', ResourceConfig(Node)),
            Lock: ('locks', ResourceConfig(Lock))
        }

    def test_lock_schema(self):
        schema = self._render(Lock)['schema']
        self.assertIn('node_id', schema)
        self.assertIn('node', schema)
        self.assertEqual(schema['node_id'], {
            'type': 'integer',
            'unique': True,
            'coerce': int,
            'nullable': False,
            'required': False
        })
        self.assertEqual(schema['node'], {
            'type': 'integer',
            'coerce': int,
            'data_relation': {
                'resource': 'nodes',
                'field': 'id'
            },
            'local_id_field': 'node_id',
            'nullable': False,
            'required': True,
            'unique': True
        })
