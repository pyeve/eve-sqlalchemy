# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from eve_sqlalchemy.config import ResourceConfig

from .. import BaseModel
from . import ResourceConfigTestCase

Base = declarative_base(cls=BaseModel)


association_table = Table(
    'association', Base.metadata,
    Column('left_id', Integer, ForeignKey('left.id')),
    Column('right_id', Integer, ForeignKey('right.id'))
)


class Parent(Base):
    __tablename__ = 'left'
    id = Column(Integer, primary_key=True)
    children = relationship('Child', secondary=association_table,
                            backref='parents')


class Child(Base):
    __tablename__ = 'right'
    id = Column(Integer, primary_key=True)


class TestManyToManyRelationship(ResourceConfigTestCase):
    """Test a basic Many-To-Many relationship in SQLAlchemy.

    The model definitions are taken from the official documentation:
    http://docs.sqlalchemy.org/en/rel_1_1/orm/basic_relationships.html#many-to-many
    """

    def setUp(self):
        super(TestManyToManyRelationship, self).setUp()
        self._related_resource_configs = {
            Child: ('children', ResourceConfig(Child)),
            Parent: ('parents', ResourceConfig(Parent))
        }

    def test_parent_projection(self):
        projection = self._render(Parent)['datasource']['projection']
        self.assertEqual(projection, {'_etag': 0, 'id': 1, 'children': 1})

    def test_child_projection(self):
        projection = self._render(Child)['datasource']['projection']
        self.assertEqual(projection, {'_etag': 0, 'id': 1, 'parents': 1})

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
        self.assertIn('parents', schema)
        self.assertEqual(schema['parents'], {
            'type': 'list',
            'schema': {
                'type': 'integer',
                'data_relation': {
                    'resource': 'parents',
                    'field': 'id'
                },
                'nullable': True
            }
        })
