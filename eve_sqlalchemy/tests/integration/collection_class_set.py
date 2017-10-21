# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, String, Table, func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from eve_sqlalchemy.config import DomainConfig, ResourceConfig
from eve_sqlalchemy.tests import TestMinimal

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    _created = Column(DateTime, default=func.now())
    _updated = Column(DateTime, default=func.now(), onupdate=func.now())
    _etag = Column(String(40))


association_table = Table(
    'association', Base.metadata,
    Column('left_id', Integer, ForeignKey('left.id')),
    Column('right_id', Integer, ForeignKey('right.id'))
)


class Parent(BaseModel):
    __tablename__ = 'left'
    id = Column(Integer, primary_key=True)
    children = relationship("Child", secondary=association_table,
                            backref="parents", collection_class=set)


class Child(BaseModel):
    __tablename__ = 'right'
    id = Column(Integer, primary_key=True)


SETTINGS = {
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'RESOURCE_METHODS': ['GET', 'POST', 'DELETE'],
    'ITEM_METHODS': ['GET', 'PATCH', 'DELETE', 'PUT'],
    'DOMAIN': DomainConfig({
        'parents': ResourceConfig(Parent),
        'children': ResourceConfig(Child),
    }).render()
}


class TestCollectionClassSet(TestMinimal):

    def setUp(self, url_converters=None):
        super(TestCollectionClassSet, self).setUp(
            SETTINGS, url_converters, Base)

    def bulk_insert(self):
        self.app.data.insert('children', [{'id': k} for k in range(1, 5)])
        self.app.data.insert('parents', [
            {'id': 1, 'children': set([1, 2])},
            {'id': 2, 'children': set()}])

    def test_get_parents(self):
        response, status = self.get('parents')
        self.assert200(status)
        self.assertEqual(len(response['_items']), 2)
        self.assertEqual(response['_items'][0]['children'], [1, 2])
        self.assertEqual(response['_items'][1]['children'], [])

    def test_post_parent(self):
        _, status = self.post('parents', {'id': 3, 'children': [3]})
        self.assert201(status)
        response, status = self.get('parents', item=3)
        self.assert200(status)
        self.assertEqual(response['children'], [3])

    def test_patch_parent(self):
        etag = self.get('parents', item=2)[0]['_etag']
        _, status = self.patch('/parents/2', {'children': [3, 4]},
                               [('If-Match', etag)])
        self.assert200(status)
        response, _ = self.get('parents', item=2)
        self.assertEqual(response['children'], [3, 4])
