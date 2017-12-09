# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sqlalchemy.dialects.postgresql as postgresql
from eve.exceptions import ConfigException
from sqlalchemy import types
from sqlalchemy.ext.declarative.api import DeclarativeMeta


class FieldConfig(object):

    def __init__(self, name, model, mapper):
        self._name = name
        self._model = model
        self._mapper = mapper
        self._field = getattr(model, name)

    def render(self, related_resource_configs):
        self._related_resource_configs = related_resource_configs
        return self._render()

    def _get_field_type(self, sqla_column):
        sqla_type_mapping = {
            postgresql.JSON: 'json',
            types.Boolean: 'boolean',
            types.DATETIME: 'datetime',
            types.Date: 'datetime',
            types.DateTime: 'datetime',
            types.Float: 'float',
            types.Integer: 'integer',
            types.JSON: 'json',
            types.PickleType: None,
        }
        for sqla_type, field_type in sqla_type_mapping.items():
            if isinstance(sqla_column.type, sqla_type):
                return field_type
        return 'string'


class ColumnFieldConfig(FieldConfig):

    def __init__(self, *args, **kwargs):
        super(ColumnFieldConfig, self).__init__(*args, **kwargs)
        self._sqla_column = self._field.expression

    def _render(self):
        return {k: v for k, v in {
            'type': self._get_field_type(self._sqla_column),
            'nullable': self._get_field_nullable(),
            'required': self._get_field_required(),
            'unique': self._get_field_unique(),
            'maxlength': self._get_field_maxlength(),
            'default': self._get_field_default(),
        }.items() if v is not None}

    def _get_field_nullable(self):
        return getattr(self._sqla_column, 'nullable', True)

    def _has_server_default(self):
        return bool(getattr(self._sqla_column, 'server_default'))

    def _get_field_required(self):
        autoincrement = (self._sqla_column.primary_key
                         and self._sqla_column.autoincrement
                         and isinstance(self._sqla_column.type, types.Integer))
        return not (self._get_field_nullable()
                    or autoincrement
                    or self._has_server_default())

    def _get_field_unique(self):
        return getattr(self._sqla_column, 'unique', None)

    def _get_field_maxlength(self):
        try:
            return self._sqla_column.type.length
        except AttributeError:
            return None

    def _get_field_default(self):
        try:
            return self._sqla_column.default.arg
        except AttributeError:
            return None


class RelationshipFieldConfig(FieldConfig):

    def __init__(self, *args, **kwargs):
        super(RelationshipFieldConfig, self).__init__(*args, **kwargs)
        self._relationship = self._mapper.relationships[self._name]

    def _render(self):
        if self._relationship.uselist:
            if self._relationship.collection_class == set:
                return {
                    'type': 'set',
                    'coerce': set,
                    'schema': self._get_foreign_key_definition()
                }
            else:
                return {
                    'type': 'list',
                    'schema': self._get_foreign_key_definition()
                }
        else:
            field_def = self._get_foreign_key_definition()
            # This is a workaround to support PUT with integer ids.
            # TODO: Investigate this and fix it properly.
            if field_def['type'] == 'integer':
                field_def['coerce'] = int
            return field_def

    def _get_foreign_key_definition(self):
        resource, resource_config = self._get_resource()
        if len(self.local_foreign_keys) > 0:
            # TODO: does this make sense?
            remote_column = tuple(self._relationship.remote_side)[0]
            local_column = tuple(self.local_foreign_keys)[0]
        else:
            # TODO: Would item_lookup_field make sense here, too?
            remote_column = getattr(resource_config.model,
                                    resource_config.id_field)
            local_column = None
        field_def = {
            'data_relation': {
                'resource': resource,
                'field': remote_column.key
            },
            'type': self._get_field_type(remote_column),
            'nullable': True
        }
        if local_column is not None:
            field_def['local_id_field'] = local_column.key
            if not getattr(local_column, 'nullable', True):
                field_def['required'] = True
                field_def['nullable'] = False
            if getattr(local_column, 'unique') or \
               getattr(local_column, 'primary_key'):
                field_def['unique'] = True
        return field_def

    def _get_resource(self):
        try:
            return self._related_resource_configs[(self._model, self._name)]
        except LookupError:
            try:
                arg = self._relationship.argument
                if isinstance(arg, DeclarativeMeta):
                    return self._related_resource_configs[arg]
                elif callable(arg):
                    return self._related_resource_configs[arg()]
                else:
                    return self._related_resource_configs[arg.class_]
            except LookupError:
                raise ConfigException(
                    'Cannot determine related resource for {model}.{field}. '
                    'Please specify `related_resources` manually.'
                    .format(model=self._model.__name__, field=self._name))

    @property
    def local_foreign_keys(self):
        return set(c for c in self._relationship.local_columns
                   if len(c.expression.foreign_keys) > 0)


class AssociationProxyFieldConfig(FieldConfig):

    def _render(self):
        resource, resource_config = self._get_resource()
        remote_column = getattr(resource_config.model,
                                self._field.value_attr)
        remote_column_type = self._get_field_type(remote_column)
        return {
            'type': 'list',
            'schema': {
                'type': remote_column_type,
                'data_relation': {
                    'resource': resource,
                    'field': remote_column.key
                }
            }
        }

    def _get_resource(self):
        try:
            return self._related_resource_configs[(self._model, self._name)]
        except LookupError:
            try:
                relationship = self._mapper.relationships[
                    self._field.target_collection]
                return self._related_resource_configs[relationship.argument()]
            except LookupError:
                model = self._mapper.class_
                raise ConfigException(
                    'Cannot determine related resource for {model}.{field}. '
                    'Please specify `related_resources` manually.'
                    .format(model=model.__name__,
                            field=self._name))

    @property
    def proxied_relationship(self):
        return self._field.target_collection


class ColumnPropertyFieldConfig(FieldConfig):

    def _render(self):
        return {
            'type': self._get_field_type(self._field.expression),
            'readonly': True,
        }


class HybridPropertyFieldConfig(FieldConfig):

    def _render(self):
        # TODO: For now all hybrid properties will be returned as strings.
        # Investigate and see if we actually can do better than this.
        return {
            'type': 'string',
            'readonly': True,
        }
