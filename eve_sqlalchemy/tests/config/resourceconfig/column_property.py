# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property

from .. import BaseModel
from . import ResourceConfigTestCase

Base = declarative_base(cls=BaseModel)


class User(Base):
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    fullname = column_property(firstname + " " + lastname)


class TestColumnProperty(ResourceConfigTestCase):
    """Test a basic column property in SQLAlchemy.

    The model definition is taken from the official documentation:
    http://docs.sqlalchemy.org/en/rel_1_1/orm/mapping_columns.html#using-column-property-for-column-level-options
    """

    def test_appears_in_projection(self):
        projection = self._render(User)['datasource']['projection']
        self.assertIn('fullname', projection.keys())
        self.assertEqual(projection['fullname'], 1)

    def test_schema(self):
        schema = self._render(User)['schema']
        self.assertIn('fullname', schema.keys())
        self.assertEqual(schema['fullname'], {
            'type': 'string',
            'readonly': True
        })
