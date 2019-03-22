# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from .. import BaseModel
from . import ResourceConfigTestCase

Base = declarative_base(cls=BaseModel)


class SomeModel(Base):
    id = Column(Integer, primary_key=True)
    unique = Column(String, unique=True)
    non_unique = Column(String)


class TestDatasource(ResourceConfigTestCase):

    def test_set_source_to_model_name(self):
        endpoint_def = self._render(SomeModel)
        self.assertEqual(endpoint_def['datasource']['source'], 'SomeModel')

    def test_projection_for_regular_columns(self):
        endpoint_def = self._render(SomeModel)
        self.assertEqual(endpoint_def['datasource']['projection'], {
            '_etag': 0,
            'id': 1,
            'unique': 1,
            'non_unique': 1,
        })

    def test_projection_with_custom_automatically_handled_fields(self):
        self._created = '_date_created'
        self._updated = '_last_updated'
        self._etag = 'non_unique'
        endpoint_def = self._render(SomeModel)
        self.assertEqual(endpoint_def['datasource']['projection'], {
            'non_unique': 0,
            'id': 1,
            'unique': 1,
        })
