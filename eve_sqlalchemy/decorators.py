# -*- coding: utf-8 -*-
"""
    Decorators for schema registering

    :copyright: (c) 2013 by Andrew Mleczko
    :license: BSD, see LICENSE for more details.
"""
from __future__ import unicode_literals

from sqlalchemy.sql import expression
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy.ext.associationproxy import ASSOCIATION_PROXY
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy import types, inspect
import sqlalchemy.dialects.postgresql as postgresql
from sqlalchemy import schema as sqla_schema
from eve.utils import config

from .utils import dict_update


__all__ = ['registerSchema']

sqla_type_mapping = {
    types.Integer: 'integer',
    types.Float: 'float',
    types.Boolean: 'boolean',
    types.Date: 'datetime',
    types.DateTime: 'datetime',
    types.DATETIME: 'datetime',
    types.PickleType: None
}


def get_sqla_type_mapping():
    try:
        sqla_type_mapping[postgresql.JSON] = 'json'
    except AttributeError:
        # NOTE(Gonéri): JSON has been introduced in SQLAlchemy 0.9.0.
        pass
    # TODO: Add the remaining sensible SQL types
    return sqla_type_mapping


def lookup_column_type(intype):
    for sqla_type, api_type in get_sqla_type_mapping().items():
        if isinstance(intype, sqla_type):
            return api_type
    return 'string'


class registerSchema(object):
    """
    Class decorator that scans a SQLAlchemy Base class, prepare an eve schema
    and attach it to the class attributes.
    """

    def __init__(self, resource=None, **kwargs):
        self.resource = resource

    def __call__(self, cls_):
        resource = self.resource or cls_.__name__.lower()

        domain = {
            resource: {
                'schema': {},
                'datasource': {'source': cls_.__name__},
                'id_field': config.ID_FIELD,
                'item_lookup': True,
                'item_lookup_field': config.ID_FIELD,
                'item_url': 'regex("[0-9]+")'
            }
        }
        projection = domain[resource]['datasource']['projection'] = {}

        if hasattr(cls_, '_eve_resource'):
            dict_update(domain[resource], cls_._eve_resource)

        all_orm_descriptors = inspect(cls_).all_orm_descriptors

        for desc in all_orm_descriptors:
            if isinstance(desc, InstrumentedAttribute):
                prop = desc.property
                if prop.key in (config.LAST_UPDATED,
                                config.DATE_CREATED,
                                config.ETAG):
                    continue
                if hasattr(prop, 'columns') and \
                   hasattr(prop.columns[0], 'foreign_keys') and \
                   len(prop.columns[0].foreign_keys) > 0:
                    continue
                schema = domain[resource]['schema'][prop.key] = {}
                self.register_column(prop, schema, projection)

            elif desc.extension_type is HYBRID_PROPERTY:
                schema = domain[resource]['schema'][desc.__name__] = {}
                schema['unique'] = False
                schema['required'] = False
                schema['readonly'] = True
                schema['type'] = 'string'
                projection[desc.__name__] = 1

        # Creation of a dictionnary of known attribute types (key ->
        # descriptor) based on the presence of the 'extension_type' attribute.
        attributes = dict(
            (key, desc)
            for key, desc in cls_.__dict__.items()
            if getattr(desc, 'extension_type', False)
        )

        # Filter the attributes dictionnary to get only association proxies
        association_proxies = dict(
            (key, desc)
            for key, desc in attributes.items()
            if desc.extension_type is ASSOCIATION_PROXY
        )

        # Register association proxies according their 'remote_attr'
        # attribute (usually a remote relationship in the association table).
        for name, desc in association_proxies.items():
            # Note(Kevin Roy): The direct call of __get__() is needed in order
            # to set the 'owning_class' attribute and getting 'remote_attr'
            # else we get an error according to corresponding source of
            # association_proxy.

            desc.__get__(None, cls_)
            if hasattr(desc.remote_attr.property, 'target'):
                r = desc.remote_attr.property.target.name
            else:
                r = desc.remote_attr.property.key

            remote_id_column = list(desc.remote_attr.property.remote_side)[0]

            schema = domain[resource]['schema'][name] = {}
            schema['type'] = 'list'
            schema['schema'] = {
                'type': lookup_column_type(remote_id_column.type),
                'data_relation': {
                    'resource': r
                }
            }
            projection[name] = 1
            projection[desc.target_collection] = 0

        cls_._eve_schema = domain
        return cls_

    @staticmethod
    def register_column(prop, schema, projection):
        if hasattr(prop, 'remote_side'):
            id_column = list(prop.local_columns)[0]
            remote_id_column = list(prop.remote_side)[0]
            schema.update(registerSchema._get_data_relation_schema(
                id_column, remote_id_column))
            schema['local_id_field'] = id_column.key
            projection[prop.key] = 1
        else:
            col = prop.columns[0]
            projection[prop.key] = 1
            column_e = expression.ColumnElement
            if isinstance(col, sqla_schema.Column):
                if col.nullable:
                    schema['nullable'] = True
                if lookup_column_type(col.type):
                    schema['type'] = lookup_column_type(col.type)
                schema['unique'] = col.primary_key or col.unique or False
                schema['required'] = not col.nullable \
                    if not col.primary_key else False
                if hasattr(col.type, 'length') and col.type.length:
                    schema['maxlength'] = col.type.length
                if col.default is not None and hasattr(col.default, 'arg'):
                    schema['default'] = col.default.arg
                    col.default = None
                # We add coercion for integer ids to allow PUT
                if col.primary_key and schema['type'] == 'integer':
                    schema['coerce'] = int
            elif isinstance(col, column_e):
                if lookup_column_type(col.type):
                    schema['type'] = lookup_column_type(col.type)
            else:
                schema['type'] = 'string'

    @staticmethod
    def _get_data_relation_schema(id_column, remote_id_column):
        schema = {}
        if id_column.nullable:
            schema['nullable'] = True
        # schema['type'] = ['dict']
        if lookup_column_type(id_column.type):
            schema['type'] = lookup_column_type(id_column.type)
            if schema['type'] == 'integer':
                schema['coerce'] = int
        schema['unique'] = \
            id_column.primary_key or id_column.unique or False
        schema['required'] = not id_column.nullable \
            if not id_column.primary_key else False
        schema['data_relation'] = {
            'resource': remote_id_column.table.name,
            'field': remote_id_column.key,
        }
        return schema
