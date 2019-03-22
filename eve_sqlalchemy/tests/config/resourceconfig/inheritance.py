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


class Thing(Node):
    id = Column(Integer, ForeignKey('node.id'), primary_key=True,
                nullable=False)
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship('Group', uselist=False, back_populates='things')


class Group(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    things = relationship('Thing', back_populates='group')


class TestPolymorphy(ResourceConfigTestCase):

    def setUp(self):
        super(TestPolymorphy, self).setUp()
        self._related_resource_configs = {
            Node: ('nodes', ResourceConfig(Node)),
            Thing: ('things', ResourceConfig(Thing)),
            Group: ('groups', ResourceConfig(Group)),
        }

    def test_node_schema(self):
        schema = self._render(Node)['schema']
        self.assertIn('id', schema)

    def test_thing_schema(self):
        schema = self._render(Thing)['schema']
        self.assertIn('id', schema)

    def test_group_schema(self):
        schema = self._render(Group)['schema']
        self.assertIn('id', schema)
