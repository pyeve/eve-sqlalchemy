# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as postgresql
from sqlalchemy import Column, types
from sqlalchemy.ext.declarative import declarative_base

from .. import BaseModel
from . import ResourceConfigTestCase

Base = declarative_base(cls=BaseModel)


class SomeModel(Base):
    id = Column(types.Integer, primary_key=True)
    a_boolean = Column(types.Boolean, nullable=False)
    a_date = Column(types.Date, unique=True)
    a_datetime = Column(types.DateTime)
    a_float = Column(types.Float)
    a_json = Column(types.JSON)
    another_json = Column(postgresql.JSON)
    a_pickle = Column(types.PickleType)
    a_string = Column(types.String(42), default='H2G2')
    _internal = Column(types.Integer)
    a_server_default_col = Column(types.Integer, server_default=sa.text('0'))


class StringPK(Base):
    id = Column(types.String, primary_key=True)


class IntegerPKWithoutAI(Base):
    id = Column(types.Integer, primary_key=True, autoincrement=False)


class TestSchema(ResourceConfigTestCase):

    def test_all_columns_appear_in_schema(self):
        schema = self._render(SomeModel)['schema']
        self.assertEqual(set(schema.keys()),
                         set(('id', 'a_boolean', 'a_date', 'a_datetime',
                              'a_float', 'a_json', 'another_json',
                              'a_pickle', 'a_string', 'a_server_default_col')))

    def test_field_types(self):
        schema = self._render(SomeModel)['schema']
        self.assertEqual(schema['id']['type'], 'integer')
        self.assertEqual(schema['a_boolean']['type'], 'boolean')
        self.assertEqual(schema['a_date']['type'], 'datetime')
        self.assertEqual(schema['a_datetime']['type'], 'datetime')
        self.assertEqual(schema['a_float']['type'], 'float')
        self.assertEqual(schema['a_json']['type'], 'json')
        self.assertEqual(schema['another_json']['type'], 'json')
        self.assertNotIn('type', schema['a_pickle'])

    def test_nullable(self):
        schema = self._render(SomeModel)['schema']
        self.assertTrue(schema['a_float']['nullable'])
        self.assertFalse(schema['id']['nullable'])
        self.assertFalse(schema['a_boolean']['nullable'])

    def test_required(self):
        schema = self._render(SomeModel)['schema']
        self.assertTrue(schema['a_boolean']['required'])
        self.assertFalse(schema['a_float']['required'])
        # As the primary key is an integer column, it will have
        # autoincrement='auto' per default (see SQLAlchemy docs for
        # details). As such, it is not required.
        self.assertFalse(schema['id']['required'])
        self.assertFalse(schema['a_server_default_col']['required'])

    def test_required_string_pk(self):
        schema = self._render(StringPK)['schema']
        self.assertTrue(schema['id']['required'])

    def test_required_integer_pk_without_autoincrement(self):
        schema = self._render(IntegerPKWithoutAI)['schema']
        self.assertTrue(schema['id']['required'])

    def test_unique(self):
        schema = self._render(SomeModel)['schema']
        self.assertTrue(schema['id']['unique'])
        self.assertTrue(schema['a_date']['unique'])
        self.assertNotIn('unique', schema['a_float'])

    def test_maxlength(self):
        schema = self._render(SomeModel)['schema']
        self.assertEqual(schema['a_string']['maxlength'], 42)
        self.assertNotIn('maxlength', schema['id'])

    def test_default(self):
        schema = self._render(SomeModel)['schema']
        self.assertEqual(schema['a_string']['default'], 'H2G2')
        self.assertNotIn('default', schema['a_boolean'])

    def test_coerce(self):
        schema = self._render(SomeModel)['schema']
        self.assertEqual(schema['id']['coerce'], int)
        schema = self._render(IntegerPKWithoutAI)['schema']
        self.assertEqual(schema['id']['coerce'], int)
        schema = self._render(StringPK)['schema']
        self.assertNotIn('coerce', schema['id'])

    def test_default_is_not_unset(self):
        self._render(SomeModel)
        self.assertIsNotNone(SomeModel.a_string.default)
        self.assertEqual(SomeModel.a_string.default.arg, 'H2G2')
