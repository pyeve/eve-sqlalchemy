# -*- coding: utf-8 -*-
"""
    This module implements the SQLAlchemy Validator class,
    used to validate that objects incoming via POST/PATCH requests
    conform to the API domain.
    An extension of Cerberus Validator.

    :copyright: (c) 2013 by Nicola Iarocci, Andrew Mleczko and
                Tomasz Jezierski (Tefnet)
    :license: BSD, see LICENSE for more details.
"""
from __future__ import unicode_literals

import collections
import copy

from cerberus import Validator
from eve.utils import config, str_type
from eve.versioning import (
    get_data_version_relation_document, missing_version_field,
)
from flask import current_app as app

from eve_sqlalchemy.utils import dict_update, remove_none_values


class ValidatorSQL(Validator):
    """ A cerberus.Validator subclass adding the `unique` constraint to
    Cerberus standard validation. For documentation please refer to the
    Validator class of the eve.io.mongo package.
    """

    def __init__(self, schema, resource=None, **kwargs):
        self.resource = resource
        self._id = None
        self._original_document = None
        kwargs['transparent_schema_rules'] = True
        super(ValidatorSQL, self).__init__(schema, **kwargs)
        if resource:
            self.allow_unknown = config.DOMAIN[resource]['allow_unknown']

    def validate_update(self, document, _id, original_document=None):
        self._id = _id
        self._original_document = original_document
        return super(ValidatorSQL, self).validate_update(document)

    def validate_replace(self, document, _id, original_document=None):
        self._id = _id
        self._original_document = original_document
        return self.validate(document)

    def _validate_unique(self, unique, field, value):
        if unique:
            id_field = config.DOMAIN[self.resource]['id_field']
            if field == id_field and value == self._id:
                return
            elif field != id_field and self._id is not None:
                query = {field: value, id_field: '!= \'%s\'' % self._id}
            else:
                query = {field: value}
            if app.data.find_one(self.resource, None, **query):
                self._error(field, "value '%s' is not unique" % value)

    def _validate_data_relation(self, data_relation, field, value):
        if 'version' in data_relation and data_relation['version'] is True:
            value_field = data_relation['field']
            version_field = app.config['VERSION']

            # check value format
            if isinstance(value, dict) and value_field in value and \
               version_field in value:
                resource_def = config.DOMAIN[data_relation['resource']]
                if resource_def['versioning'] is False:
                    self._error(field, ("can't save a version with "
                                        "data_relation if '%s' isn't "
                                        "versioned") %
                                data_relation['resource'])
                else:
                    # support late versioning
                    if value[version_field] == 0:
                        # there is a chance this document hasn't been saved
                        # since versioning was turned on
                        search = missing_version_field(data_relation, value)
                    else:
                        search = get_data_version_relation_document(
                            data_relation, value)
                    if not search:
                        self._error(field, ("value '%s' must exist in resource"
                                            " '%s', field '%s' at version "
                                            "'%s'.") % (
                                    value[value_field],
                                    data_relation['resource'],
                                    data_relation['field'],
                                    value[version_field]))
            else:
                self._error(field, ("versioned data_relation must be a dict "
                                    "with fields '%s' and '%s'") %
                            (value_field, version_field))
        else:
            query = {data_relation['field']: value}
            if not app.data.find_one(data_relation['resource'], None, **query):
                self._error(field, ("value '%s' must exist in resource '%s', "
                                    "field '%s'") %
                            (value, data_relation['resource'],
                             data_relation['field']))

    def _validate_type_objectid(self, field, value):
        """
        This field doesn't have a meaning in SQL
        """
        pass

    def _validate_type_json(self, field, value):
        """ Enables validation for `json` schema attribute.

        :param field: field name.
        :param value: field value.
        """
        pass

    def _validate_readonly(self, read_only, field, value):
        # Copied from eve/io/mongo/validation.py.
        original_value = self._original_document.get(field) \
            if self._original_document else None
        if value != original_value:
            super(ValidatorSQL, self)._validate_readonly(read_only, field,
                                                         value)

    def _validate_dependencies(self, document, dependencies, field,
                               break_on_error=False):
        # Copied from eve/io/mongo/validation.py, with slight modifications.

        if dependencies is None:
            return True

        if isinstance(dependencies, str_type):
            dependencies = [dependencies]

        defaults = {}
        for d in dependencies:
            root = d.split('.')[0]
            default = self.schema[root].get('default')
            if default and root not in document:
                defaults[root] = default

        if isinstance(dependencies, collections.Mapping):
            # Only evaluate dependencies that don't have *valid* defaults
            for k, v in defaults.items():
                if v in dependencies[k]:
                    del(dependencies[k])
        else:
            # Only evaluate dependencies that don't have defaults values
            dependencies = [d for d in dependencies if d not in
                            defaults.keys()]

        dcopy = None
        if self._original_document:
            dcopy = copy.copy(document)
            # Use dict_update and remove_none_values from utils, so existing
            # values in document don't get overridden by the original document
            # and None values are removed. Otherwise handling in parent method
            # does not work as expected.
            dict_update(dcopy, self._original_document)
            remove_none_values(dcopy)
        return super(ValidatorSQL, self)._validate_dependencies(
            dcopy or document, dependencies, field, break_on_error)

    def _error(self, field, _error):
        # Copied from eve/io/mongo/validation.py.
        super(ValidatorSQL, self)._error(field, _error)
        if config.VALIDATION_ERROR_AS_LIST:
            err = self._errors[field]
            if not isinstance(err, list):
                self._errors[field] = [err]
