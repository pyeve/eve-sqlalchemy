# -*- coding: utf-8 -*-
"""
    Helpers and utils functions

    :copyright: (c) 2013 by Andrew Mleczko and Tomasz Jezierski (Tefnet)
    :license: BSD, see LICENSE for more details.

"""
from __future__ import unicode_literals

import ast
import collections
import copy
import re

from eve.utils import config
from sqlalchemy.ext.declarative.api import DeclarativeMeta


def dict_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping) and \
           k in d and isinstance(d[k], collections.Mapping):
            dict_update(d[k], v)
        elif k not in d:
            d[k] = u[k]


def remove_none_values(dict_):
    for k, v in list(dict_.items()):
        if v is None:
            del(dict_[k])


def validate_filters(where, resource):
    allowed = config.DOMAIN[resource]['allowed_filters']
    if '*' not in allowed:
        for filt in where:
            key = filt.left.key
            if key not in allowed:
                return "filter on '%s' not allowed" % key
    return None


def sqla_object_to_dict(obj, fields):
    """ Creates a dict containing copies of the requested fields from the
    SQLAlchemy query result """
    if config.LAST_UPDATED not in fields:
        fields.append(config.LAST_UPDATED)
    if config.DATE_CREATED not in fields:
        fields.append(config.DATE_CREATED)
    if config.ETAG not in fields \
            and getattr(config, 'IF_MATCH', True):
        fields.append(config.ETAG)

    result = {}
    for field in map(lambda f: f.split('.', 1)[0], fields):
        try:
            val = obj.__getattribute__(field)

            # If association proxies are embedded, their values must be copied
            # since they are garbage collected when Eve try to encode the
            # response.
            if hasattr(val, 'copy'):
                val = val.copy()

            result[field] = _sanitize_value(val)
        except AttributeError:
            # Ignore if the requested field does not exist
            # (may be wrong embedding parameter)
            pass

    remove_none_values(result)
    return result


def _sanitize_value(value):
    if isinstance(value.__class__, DeclarativeMeta):
        return _get_id(value)
    elif isinstance(value, collections.Mapping):
        return dict([(k, _sanitize_value(v)) for k, v in value.items()])
    elif isinstance(value, collections.MutableSequence):
        return [_sanitize_value(v) for v in value]
    elif isinstance(value, collections.Set):
        return set(_sanitize_value(v) for v in value)
    else:
        return copy.copy(value)


def _get_id(obj):
    resource = list(obj._eve_schema.keys())[0]
    return getattr(obj, obj._eve_schema[resource]['id_field'])


def extract_sort_arg(req):
    if req.sort:
        if re.match('^[-,\w]+$', req.sort):
            arg = []
            for s in req.sort.split(','):
                if s.startswith('-'):
                    arg.append([s[1:], -1])
                else:
                    arg.append([s])
            return arg
        else:
            return ast.literal_eval(req.sort)
    else:
        return None
