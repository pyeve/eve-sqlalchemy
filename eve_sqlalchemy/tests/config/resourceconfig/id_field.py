# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import TestCase

from eve.exceptions import ConfigException
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from eve_sqlalchemy.config import ResourceConfig

from .. import BaseModel, call_for

Base = declarative_base(cls=BaseModel)


class SingleColumnPrimaryKey(Base):
    id = Column(Integer, primary_key=True)
    unique = Column(String, unique=True)
    non_unique = Column(String)


class MultiColumnPrimaryKey(Base):
    id_1 = Column(Integer, primary_key=True)
    id_2 = Column(Integer, primary_key=True)
    unique = Column(String, unique=True)
    non_unique = Column(String)


class TestIDField(TestCase):
    """
    Test setting/deducing the resource-level `id_field` setting.

    There is no need to test the case where we have a model without a primary
    key, as such a model cannot be defined using sqlalchemy.ext.declarative.
    """

    def test_set_to_primary_key_by_default(self):
        rc = ResourceConfig(SingleColumnPrimaryKey)
        self.assertEqual(rc.id_field, 'id')

    def test_set_to_primary_key_by_user(self):
        rc = ResourceConfig(SingleColumnPrimaryKey, id_field='id')
        self.assertEqual(rc.id_field, 'id')

    @call_for(SingleColumnPrimaryKey, MultiColumnPrimaryKey)
    def test_fail_for_non_existent_user_specified_id_field(self, model):
        with self.assertRaises(ConfigException) as cm:
            ResourceConfig(model, id_field='foo')
        self.assertIn('{}.foo does not exist.'.format(model.__name__),
                      str(cm.exception))

    @call_for(SingleColumnPrimaryKey, MultiColumnPrimaryKey)
    def test_fail_for_non_unique_user_specified_id_field(self, model):
        with self.assertRaises(ConfigException) as cm:
            ResourceConfig(model, id_field='non_unique')
        self.assertIn('{}.non_unique is not unique.'.format(model.__name__),
                      str(cm.exception))

    def test_fail_without_user_specified_id_field(self):
        model = MultiColumnPrimaryKey
        with self.assertRaises(ConfigException) as cm:
            ResourceConfig(model)
        self.assertIn("{}'s primary key consists of zero or multiple columns, "
                      "thus we cannot deduce which one to use."
                      .format(model.__name__), str(cm.exception))

    def test_fail_with_user_specified_id_field_as_subset_of_primary_key(self):
        model = MultiColumnPrimaryKey
        with self.assertRaises(ConfigException) as cm:
            ResourceConfig(model, id_field='id_1')
        self.assertIn('{}.id_1 is not unique.'.format(model.__name__),
                      str(cm.exception))
