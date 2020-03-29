# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from eve_sqlalchemy.config import ResourceConfig

from .. import BaseModel
from . import ResourceConfigTestCase

Base = declarative_base(cls=BaseModel)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    kw = relationship("Keyword", secondary=lambda: userkeywords_table)

    def __init__(self, name):
        self.name = name

    keywords = association_proxy('kw', 'keyword')


class Keyword(Base):
    __tablename__ = 'keyword'
    id = Column(Integer, primary_key=True)
    keyword = Column('keyword', String(64), unique=True, nullable=False)

    def __init__(self, keyword):
        self.keyword = keyword


userkeywords_table = Table(
    'userkeywords', Base.metadata,
    Column('user_id', Integer, ForeignKey("user.id"), primary_key=True),
    Column('keyword_id', Integer, ForeignKey("keyword.id"), primary_key=True)
)


class TestAssociationProxy(ResourceConfigTestCase):
    """Test an Association Proxy in SQLAlchemy.

    The model definitions are taken from the official documentation:
    https://docs.sqlalchemy.org/en/rel_1_1/orm/extensions/associationproxy.html#simplifying-scalar-collections
    """

    def setUp(self):
        super(TestAssociationProxy, self).setUp()
        self._related_resource_configs = {
            User: ('users', ResourceConfig(User)),
            Keyword: ('keywords', ResourceConfig(Keyword))
        }

    def test_user_projection(self):
        projection = self._render(User)['datasource']['projection']
        self.assertEqual(projection, {'_etag': 0, 'id': 1, 'name': 1,
                                      'keywords': 1})

    def test_keyword_projection(self):
        projection = self._render(Keyword)['datasource']['projection']
        self.assertEqual(projection, {'_etag': 0, 'id': 1, 'keyword': 1})

    def test_user_schema(self):
        schema = self._render(User)['schema']
        self.assertNotIn('kw', schema)
        self.assertIn('keywords', schema)
        self.assertEqual(schema['keywords'], {
            'type': 'list',
            'schema': {
                'type': 'string',
                'data_relation': {
                    'resource': 'keywords',
                    'field': 'keyword'
                }
            }
        })

    def test_keyword_schema(self):
        schema = self._render(Keyword)['schema']
        self.assertIn('keyword', schema)
        self.assertEqual(schema['keyword'], {
            'type': 'string',
            'unique': True,
            'maxlength': 64,
            'required': True,
            'nullable': False
        })
