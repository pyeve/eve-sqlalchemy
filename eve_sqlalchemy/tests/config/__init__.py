# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sqlalchemy.ext.declarative import declared_attr

from eve_sqlalchemy.declarative import BaseModel


def call_for(*args):
    def decorator(f):
        def loop(self):
            for arg in args:
                f(self, arg)
        return loop
    return decorator


class BaseModel(BaseModel):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
