# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from eve_sqlalchemy.config import ResourceConfig

from .. import BaseModel
from . import ResourceConfigTestCase

Base = declarative_base(cls=BaseModel)


class Parent(Base):
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey('child.id'))
    child = relationship("Child")


class Child(Base):
    id = Column(Integer, primary_key=True)


class TestManyToOneRelationship(ResourceConfigTestCase):
    """Test a basic Many-To-One relationship in SQLAlchemy.

    The model definitions are taken from the official documentation:
    https://docs.sqlalchemy.org/en/rel_1_1/orm/basic_relationships.html#many-to-one
    """

    def setUp(self):
        super(TestManyToOneRelationship, self).setUp()
        self._related_resource_configs = {
            Child: ('children', ResourceConfig(Child))
        }

    def test_parent_projection(self):
        projection = self._render(Parent)['datasource']['projection']
        self.assertEqual(projection, {'_etag': 0, 'id': 1, 'child': 1})

    def test_child_projection(self):
        projection = self._render(Child)['datasource']['projection']
        self.assertEqual(projection, {'_etag': 0, 'id': 1})

    def test_parent_schema(self):
        schema = self._render(Parent)['schema']
        self.assertIn('child', schema)
        self.assertEqual(schema['child'], {
            'type': 'integer',
            'coerce': int,
            'data_relation': {
                'resource': 'children',
                'field': 'id'
            },
            'local_id_field': 'child_id',
            'nullable': True
        })

    def test_child_schema(self):
        schema = self._render(Child)['schema']
        self.assertNotIn('parent', schema)
        self.assertNotIn('parent_id', schema)
