# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import TestCase

from eve.exceptions import ConfigException
from sqlalchemy import Boolean, Column, ForeignKey, Integer, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from eve_sqlalchemy.config import DomainConfig, ResourceConfig

from .. import BaseModel

Base = declarative_base(cls=BaseModel)

group_members = Table(
    'group_members', Base.metadata,
    Column('group_id', Integer, ForeignKey('group.id')),
    Column('user_id', Integer, ForeignKey('user.id'))
)


class User(Base):
    id = Column(Integer, primary_key=True)
    is_admin = Column(Boolean, default=False)


class Group(Base):
    id = Column(Integer, primary_key=True)
    members = relationship(User, secondary=group_members)
    admin_id = Column(Integer, ForeignKey('user.id'))
    admin = relationship(User)


class TestAmbiguousRelations(TestCase):

    def setUp(self):
        super(TestAmbiguousRelations, self).setUp()
        self._domain = DomainConfig({
            'users': ResourceConfig(User),
            'admins': ResourceConfig(User),
            'groups': ResourceConfig(Group)
        })

    def test_missing_related_resources_without_groups(self):
        del self._domain.resource_configs['groups']
        domain_dict = self._domain.render()
        self.assertIn('users', domain_dict)
        self.assertIn('admins', domain_dict)

    def test_missing_related_resources(self):
        with self.assertRaises(ConfigException) as cm:
            self._domain.render()
        self.assertIn('Cannot determine related resource for {}'
                      .format(Group.__name__), str(cm.exception))

    def test_two_endpoints_for_one_model(self):
        self._domain.related_resources = {
            (Group, 'members'): 'users',
            (Group, 'admin'): 'admins'
        }
        groups_schema = self._domain.render()['groups']['schema']
        self.assertEqual(groups_schema['admin']['data_relation']['resource'],
                         'admins')
