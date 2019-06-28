# -*- coding: utf-8 -*-
"""
    These classes provide a middle layer to transform a SQLAlchemy query into
    a series of object that Eve understands and can be rendered as JSON.

    :copyright: (c) 2013 by Andrew Mleczko and Tomasz Jezierski (Tefnet)
    :license: BSD, see LICENSE for more details.

"""
from __future__ import unicode_literals

from .utils import sqla_object_to_dict


class SQLAResultCollection(object):
    """
    Collection of results. The object holds onto a Flask-SQLAlchemy query
    object and serves a generator off it.

    :param query: Base SQLAlchemy query object for the requested resource
    :param fields: fields to be rendered in the response, as a list of strings
    :param spec: filter to be applied to the query
    :param sort: sorting requirements
    :param max_results: number of entries to be returned per page
    :param page: page requested
    """
    def __init__(self, query, fields, **kwargs):
        self._query = query
        self._fields = fields
        self._spec = kwargs.get('spec')
        self._sort = kwargs.get('sort')
        self._max_results = kwargs.get('max_results')
        self._page = kwargs.get('page')
        self._resource = kwargs.get('resource')
        if self._spec:
            self._query = self._query.filter(*self._spec)
        if self._sort:
            for (order_by, joins) in self._sort:
                self._query = self._query.filter(*joins).order_by(order_by)

        # save the count of items to an internal variables before applying the
        # limit to the query as that screws the count returned by it
        self._count = self._query.count()
        if self._max_results:
            self._query = self._query.limit(self._max_results)
            if self._page:
                self._query = self._query.offset((self._page - 1) *
                                                 self._max_results)

    def __iter__(self):
        for i in self._query:
            yield sqla_object_to_dict(i, self._fields)

    def count(self, **kwargs):
        return self._count
