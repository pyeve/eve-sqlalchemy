# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from eve.exceptions import ConfigException
from sqlalchemy import types
from sqlalchemy.ext.associationproxy import ASSOCIATION_PROXY
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy.sql import expression

from eve_sqlalchemy.utils import merge_dicts

from .fieldconfig import (
    AssociationProxyFieldConfig, ColumnFieldConfig, ColumnPropertyFieldConfig,
    HybridPropertyFieldConfig, RelationshipFieldConfig,
)


class ResourceConfig(object):
    """Create an Eve resource dict out of an SQLAlchemy model.

    In most cases, we can deduce all required information by inspecting the
    model. This includes setting `id_field`, `item_lookup_field` and `item_url`
    at the resource level.
    """

    def __init__(self, model, id_field=None, item_lookup_field=None):
        """Initializes the :class:`ResourceConfig` object.

        If you want to customize `id_field` or `item_lookup_field`, pass them
        to this function instead of altering the configuration at a later
        point. Other settings like `item_url` depend on them!

        :param id_field: overwrite resource-level `id_field` setting
        :param item_lookup_field: overwrite resource-level `item_lookup_field`
            setting
        """
        self.model = model
        self._mapper = self.model.__mapper__  # just for convenience
        self.id_field = id_field or self._deduce_id_field()
        self.item_lookup_field = item_lookup_field or self.id_field

    def render(self, date_created, last_updated, etag,
               related_resource_configs={}):
        """Renders the Eve resource configuration.

        :param date_created: value of `DATE_CREATED`
        :param last_updated: value of `LAST_UPDATED`
        :param etag: value of `ETAG`
        :param related_resource_configs: Mapping of SQLAlchemy models or tuples
            of model + field name to a tuple of endpoint name and
            :class:`ResourceConfig` object. This is needed to properly set up
            the relationship configuration expected by Eve.
        """
        self._ignored_fields = set(
            [f for f in self.model.__dict__ if f[0] == '_'] +
            [date_created, last_updated, etag]) - \
            set([self.id_field, self.item_lookup_field])
        field_configs = self._create_field_configs()
        return {
            'id_field': self.id_field,
            'item_lookup_field': self.item_lookup_field,
            'item_url': self.item_url,
            'schema': self._render_schema(field_configs,
                                          related_resource_configs),
            'datasource': self._render_datasource(field_configs, etag),
        }

    @property
    def id_field(self):
        return self._id_field

    @id_field.setter
    def id_field(self, id_field):
        pk_columns = [c.name for c in self._mapper.primary_key]
        if not (len(pk_columns) == 1 and pk_columns[0] == id_field):
            column = self._get_column(id_field)
            if not column.unique:
                raise ConfigException(
                    "{model}.{id_field} is not unique."
                    .format(model=self.model.__name__, id_field=id_field))
        self._id_field = id_field

    def _deduce_id_field(self):
        pk_columns = [c.name for c in self.model.__mapper__.primary_key]
        if len(pk_columns) == 1:
            return pk_columns[0]
        else:
            raise ConfigException(
                "{model}'s primary key consists of zero or multiple columns, "
                "thus we cannot deduce which one to use. Please manually "
                "specify a unique column to use as `id_field`: "
                "`ResourceConfig({model}, id_field=...)`"
                .format(model=self.model.__name__))

    @property
    def item_lookup_field(self):
        return self._item_lookup_field

    @item_lookup_field.setter
    def item_lookup_field(self, item_lookup_field):
        if item_lookup_field != self.id_field:
            column = self._get_column(item_lookup_field)
            if not column.unique:
                raise ConfigException(
                    "{model}.{item_lookup_field} is not unique."
                    .format(model=self.model.__name__,
                            item_lookup_field=item_lookup_field))
        self._item_lookup_field = item_lookup_field

    @property
    def item_url(self):
        column = self._get_column(self.item_lookup_field)
        if isinstance(column.type, types.Integer):
            return 'regex("[0-9]+")'
        else:
            return 'regex("[a-zA-Z0-9_-]+")'

    def _get_column(self, column_name):
        try:
            return self._mapper.columns[column_name]
        except KeyError:
            raise ConfigException("{model}.{column_name} does not exist."
                                  .format(model=self.model.__name__,
                                          column_name=column_name))

    def _create_field_configs(self):
        association_proxies = {
            k: AssociationProxyFieldConfig(k, self.model, self._mapper)
            for k in self._get_association_proxy_fields()}
        proxied_relationships = \
            set([p.proxied_relationship for p in association_proxies.values()])
        relationships = {
            k: RelationshipFieldConfig(k, self.model, self._mapper)
            for k in self._get_relationship_fields(proxied_relationships)}
        columns = {
            k: ColumnFieldConfig(k, self.model, self._mapper)
            for k in self._get_column_fields()}
        column_properties = {
            k: ColumnPropertyFieldConfig(k, self.model, self._mapper)
            for k in self._get_column_property_fields()}
        hybrid_properties = {
            k: HybridPropertyFieldConfig(k, self.model, self._mapper)
            for k in self._get_hybrid_property_fields()}
        return merge_dicts(association_proxies, relationships, columns,
                           column_properties, hybrid_properties)

    def _get_association_proxy_fields(self):
        return [k for k, v in self.model.__dict__.items()
                if k not in self._ignored_fields
                and getattr(v, 'extension_type', None) == ASSOCIATION_PROXY]

    def _get_relationship_fields(self, proxied_relationships):
        return (f.key for f in self._mapper.relationships
                if f.key not in self._ignored_fields | proxied_relationships)

    def _get_column_fields(self):
        # We don't include "plain" foreign keys in our schema, as embedding
        # would not work for them (except the id_field, which is always
        # included).
        # TODO: Think about this decision again and maybe implement support for
        # foreign keys without relationships.
        return (f.key for f in self._mapper.column_attrs
                if f.key not in self._ignored_fields
                and isinstance(f.expression, expression.ColumnElement)
                and (f.key == self._id_field
                     or len(f.expression.foreign_keys) == 0))

    def _get_column_property_fields(self):
        return (f.key for f in self._mapper.column_attrs
                if f.key not in self._ignored_fields
                and isinstance(f.expression, expression.Label))

    def _get_hybrid_property_fields(self):
        return [k for k, v in self.model.__dict__.items()
                if k not in self._ignored_fields
                and getattr(v, 'extension_type', None) == HYBRID_PROPERTY]

    def _render_schema(self, field_configs, related_resource_configs):
        schema = {k: v.render(related_resource_configs)
                  for k, v in field_configs.items()}
        # The id field has to be unique in all cases.
        schema[self._id_field]['unique'] = True
        # This is a workaround to support PUT for resources with integer ids.
        # TODO: Investigate this and fix it properly.
        if schema[self._item_lookup_field]['type'] == 'integer':
            schema[self._item_lookup_field]['coerce'] = int
        return schema

    def _render_datasource(self, field_configs, etag):
        projection = {k: 1 for k in field_configs.keys()}
        projection[etag] = 0  # is handled automatically based on IF_MATCH
        return {
            'source': self.model.__name__,
            'projection': projection
        }
