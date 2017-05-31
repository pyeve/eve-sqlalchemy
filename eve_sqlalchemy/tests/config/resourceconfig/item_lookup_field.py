# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import TestCase

from eve.exceptions import ConfigException
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from eve_sqlalchemy.config import ResourceConfig

from .. import BaseModel

Base = declarative_base(cls=BaseModel)


class SomeModel(Base):
    id = Column(Integer, primary_key=True)
    unique = Column(String, unique=True)
    non_unique = Column(String)


class TestItemLookupField(TestCase):
    """Test setting/deducing the resource-level `item_lookup_field` setting."""

    def test_set_to_id_field_by_default(self):
        rc = ResourceConfig(SomeModel)
        self.assertEqual(rc.item_lookup_field, rc.id_field)

    def test_set_to_user_specified_id_field_by_default(self):
        rc = ResourceConfig(SomeModel, id_field='unique')
        self.assertEqual(rc.item_lookup_field, 'unique')

    def test_set_to_user_specified_field(self):
        rc = ResourceConfig(SomeModel, item_lookup_field='unique')
        self.assertEqual(rc.item_lookup_field, 'unique')

    def test_set_to_id_field_by_user(self):
        rc = ResourceConfig(SomeModel, item_lookup_field='id')
        self.assertEqual(rc.item_lookup_field, 'id')

    def test_fail_for_non_existent_user_specified_item_lookup_field(self):
        model = SomeModel
        with self.assertRaises(ConfigException) as cm:
            ResourceConfig(model, item_lookup_field='foo')
        self.assertIn('{}.foo does not exist.'.format(model.__name__),
                      str(cm.exception))

    def test_fail_for_non_unique_user_specified_item_lookup_field(self):
        model = SomeModel
        with self.assertRaises(ConfigException) as cm:
            ResourceConfig(model, item_lookup_field='non_unique')
        self.assertIn('{}.non_unique is not unique.'.format(model.__name__),
                      str(cm.exception))
