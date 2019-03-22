# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from .. import BaseModel
from . import ResourceConfigTestCase

Base = declarative_base(cls=BaseModel)


class Interval(Base):
    id = Column(Integer, primary_key=True)
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)

    @hybrid_property
    def length(self):
        return self.end - self.start


class TestHybridProperty(ResourceConfigTestCase):
    """Test a basic hybrid property in SQLAlchemy.

    The model definition is taken from the official documentation:
    http://docs.sqlalchemy.org/en/rel_1_1/orm/extensions/hybrid.html
    """

    def test_appears_in_projection(self):
        projection = self._render(Interval)['datasource']['projection']
        self.assertIn('length', projection.keys())
        self.assertEqual(projection['length'], 1)

    def test_schema(self):
        schema = self._render(Interval)['schema']
        self.assertIn('length', schema.keys())
        self.assertEqual(schema['length'], {
            'type': 'string',
            'readonly': True
        })
