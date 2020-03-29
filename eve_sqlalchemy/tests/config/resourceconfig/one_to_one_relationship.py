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
    child = relationship("Child", uselist=False, back_populates="parent")


class Child(Base):
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'), nullable=False)
    parent = relationship("Parent", back_populates="child")


class TestOneToOneRelationship(ResourceConfigTestCase):
    """Test a basic One-To-One relationship in SQLAlchemy.

    The model definitions are taken from the official documentation:
    https://docs.sqlalchemy.org/en/rel_1_1/orm/basic_relationships.html#one-to-one
    """

    def setUp(self):
        super(TestOneToOneRelationship, self).setUp()
        self._related_resource_configs = {
            Child: ('children', ResourceConfig(Child)),
            Parent: ('parents', ResourceConfig(Parent))
        }

    def test_parent_projection(self):
        projection = self._render(Parent)['datasource']['projection']
        self.assertEqual(projection, {'_etag': 0, 'id': 1, 'child': 1})

    def test_child_projection(self):
        projection = self._render(Child)['datasource']['projection']
        self.assertEqual(projection, {'_etag': 0, 'id': 1, 'parent': 1})

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
            'nullable': True
        })
        self.assertNotIn('child_id', schema)

    def test_child_schema(self):
        schema = self._render(Child)['schema']
        self.assertIn('parent', schema)
        self.assertEqual(schema['parent'], {
            'type': 'integer',
            'coerce': int,
            'data_relation': {
                'resource': 'parents',
                'field': 'id'
            },
            'local_id_field': 'parent_id',
            'nullable': False,
            'required': True
        })
        self.assertNotIn('parent_id', schema)
