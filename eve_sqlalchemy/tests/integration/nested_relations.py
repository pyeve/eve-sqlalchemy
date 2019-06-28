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


invoice_item = Table(
    'invoice_item', Base.metadata,
    Column('invoice_id', Integer, ForeignKey('invoice.id')),
    Column('item_id', Integer, ForeignKey('item.id')),
    Column('quantity', Integer)
)


class Address(BaseModel):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    city = Column(String(64))


class Invoice(BaseModel):
    __tablename__ = 'invoice'
    id = Column(Integer, primary_key=True)
    recipient_address_id = Column(Integer, ForeignKey('address.id'),
                                  nullable=False)
    recipient_address = relationship('Address', uselist=False)
    items = relationship('Item', secondary=invoice_item,
                         backref='invoices')


class Item(BaseModel):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(256))


SETTINGS = {
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'RESOURCE_METHODS': ['GET', 'POST', 'DELETE'],
    'ITEM_METHODS': ['GET', 'PATCH', 'DELETE', 'PUT'],
    'DOMAIN': DomainConfig({
        'addresses': ResourceConfig(Address),
        'invoices': ResourceConfig(Invoice),
        'items': ResourceConfig(Item),
    }).render()
}


class TestNestedRelations(TestMinimal):

    def setUp(self, url_converters=None):
        super(TestNestedRelations, self).setUp(SETTINGS, url_converters, Base)

    def bulk_insert(self):
        self.app.data.insert('addresses', [
            {'id': 1, 'city': 'Berlin'},
            {'id': 2, 'city': 'Paris'},
        ])
        self.app.data.insert('items', [
            {'id': 1, 'name': 'Flux capacitor'},
            {'id': 2, 'name': 'Excalibur'},
            {'id': 3, 'name': 'Rice crackers'},
            {'id': 4, 'name': 'Empty box'},
        ])
        self.app.data.insert('invoices', [
            {'id': 1, 'recipient_address': 1, 'items': [1, 2]},
            {'id': 2, 'recipient_address': 2, 'items': [2]},
            {'id': 3, 'recipient_address': 1, 'items': [2, 3]},
            {'id': 4, 'recipient_address': 2, 'items': [1]},
        ])

    def test_get_items_by_invoices_recipient_addresses(self):
        self._assert_queried_ids(
            'items', '?where={"invoices.recipient_address": 1}', [1, 2, 3])
        self._assert_queried_ids(
            'items', '?where={"invoices.recipient_address": 2}', [2, 1])

    def test_get_items_by_invoices_recipient_addresses_pythonic_syntax(self):
        self._assert_queried_ids(
            'items', '?where=invoices.recipient_address==1', [1, 2, 3])
        self._assert_queried_ids(
            'items', '?where=invoices.recipient_address==2', [2, 1])

    def test_get_items_by_invoices_recipient_addresses_city(self):
        self._assert_queried_ids(
            'items', '?where={"invoices.recipient_address.city": "Berlin"}',
            [1, 2, 3])
        self._assert_queried_ids(
            'items', '?where={"invoices.recipient_address.city": "Paris"}',
            [2, 1])

    def test_get_invoices_by_item_id(self):
        self._assert_queried_ids('invoices', '?where={"items": 1}', [1, 4])

    def test_sort_invoices_by_recipient_address_city(self):
        self._assert_queried_ids(
            'invoices', '?sort=recipient_address.city', [1, 3, 2, 4])
        self._assert_queried_ids(
            'invoices', '?sort=-recipient_address.city', [2, 4, 1, 3])

    def _assert_queried_ids(self, resource, query, ids):
        response, status = self.get(resource, query)
        self.assert200(status)
        items = response['_items']
        self.assertEqual([i['id'] for i in items], ids)
