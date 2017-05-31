# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import TestCase

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from eve_sqlalchemy.config import ResourceConfig

from .. import BaseModel

Base = declarative_base(cls=BaseModel)


class SomeModel(Base):
    id = Column(Integer, primary_key=True)
    unique = Column(String, unique=True)
    non_unique = Column(String)


class TestItemUrl(TestCase):

    def test_set_to_default_regex_for_integer_item_lookup_field(self):
        rc = ResourceConfig(SomeModel)
        self.assertEqual(rc.item_url, 'regex("[0-9]+")')

    def test_set_to_default_regex_for_string_item_lookup_field(self):
        rc = ResourceConfig(SomeModel, item_lookup_field='unique')
        self.assertEqual(rc.item_url, 'regex("[a-zA-Z0-9_-]+")')
