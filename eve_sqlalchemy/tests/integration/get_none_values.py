# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base

from eve_sqlalchemy.config import DomainConfig, ResourceConfig
from eve_sqlalchemy.tests import TestMinimal

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    _created = Column(DateTime, default=func.now())
    _updated = Column(DateTime, default=func.now(), onupdate=func.now())
    _etag = Column(String(40))


class Node(BaseModel):
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True)
    none_field = Column(Integer)


SETTINGS = {
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'RESOURCE_METHODS': ['GET', 'POST', 'DELETE'],
    'ITEM_METHODS': ['GET', 'PATCH', 'DELETE', 'PUT'],
    'DOMAIN': DomainConfig({
        'nodes': ResourceConfig(Node),
    }).render()
}


class TestGetNoneValues(TestMinimal):

    def setUp(self, url_converters=None):
        super(TestGetNoneValues, self).setUp(SETTINGS, url_converters, Base)

    def bulk_insert(self):
        self.app.data.insert('nodes', [{'id': k} for k in range(1, 5)])

    def test_get_can_return_none_value(self):
        response, status = self.get('nodes/1')
        self.assert200(status)
        self.assertIn('none_field', response)
        self.assertIsNone(response['none_field'])
