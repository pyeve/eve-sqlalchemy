# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.ext.declarative import declared_attr


def call_for(*args):
    def decorator(f):
        def loop(self):
            for arg in args:
                f(self, arg)
        return loop
    return decorator


class BaseModel(object):
    __abstract__ = True
    _created = Column(DateTime, default=func.now())
    _updated = Column(DateTime, default=func.now())
    _etag = Column(String)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
