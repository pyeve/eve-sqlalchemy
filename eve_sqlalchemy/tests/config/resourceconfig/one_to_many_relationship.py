# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from eve.exceptions import ConfigException
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from eve_sqlalchemy.config import ResourceConfig

from .. import BaseModel
from . import ResourceConfigTestCase

Base = declarative_base(cls=BaseModel)


class Parent(Base):
    id = Column(Integer, primary_key=True)
    children = relationship("Child")


class Child(Base):
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'))


class TestOneToManyRelationship(ResourceConfigTestCase):
    """Test a basic One-To-Many relationship in SQLAlchemy.

    The model definitions are taken from the official documentation:
    http://docs.sqlalchemy.org/en/rel_1_1/orm/basic_relationships.html#one-to-many
    """

    def setUp(self):
        super(TestOneToManyRelationship, self).setUp()
        self._related_resource_configs = {
            Child: ('children', ResourceConfig(Child))
        }

    def test_related_resources_missing(self):
        self._related_resource_configs = {}
        model = Parent
        with self.assertRaises(ConfigException) as cm:
            self._render(model)
        self.assertIn('Cannot determine related resource for {}.children'
                      .format(model.__name__), str(cm.exception))

    def test_parent_projection(self):
        projection = self._render(Parent)['datasource']['projection']
        self.assertEqual(projection, {'_etag': 0, 'id': 1, 'children': 1})

    def test_child_projection(self):
        projection = self._render(Child)['datasource']['projection']
        self.assertEqual(projection, {'_etag': 0, 'id': 1})

    def test_parent_schema(self):
        schema = self._render(Parent)['schema']
        self.assertIn('children', schema)
        self.assertEqual(schema['children'], {
            'type': 'list',
            'schema': {
                'type': 'integer',
                'data_relation': {
                    'resource': 'children',
                    'field': 'id'
                },
                'nullable': True
            }
        })

    def test_child_schema(self):
        schema = self._render(Child)['schema']
        self.assertNotIn('parent', schema)
        self.assertNotIn('parent_id', schema)
