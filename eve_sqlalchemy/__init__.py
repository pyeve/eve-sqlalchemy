# -*- coding: utf-8 -*-
"""
    The actual implementation of the SQLAlchemy data layer.

    :copyright: (c) 2013 by Andrew Mleczko and Tomasz Jezierski (Tefnet)
    :license: BSD, see LICENSE for more details.
"""

__version__ = '0.1-dev'

import simplejson as json
import flask.ext.sqlalchemy as flask_sqlalchemy

from flask import abort
from copy import copy

from eve.io.base import ConnectionException
from eve.io.base import DataLayer
from eve.utils import config, debug_error_message, str_to_date
from .parser import parse, parse_dictionary, ParseError, sqla_op, parse_sorting
from .structures import SQLAResultCollection
from .utils import dict_update, validate_filters, sqla_object_to_dict, extract_sort_arg


db = flask_sqlalchemy.SQLAlchemy()

try:
    string_type = basestring
except NameError:
    # Python 3
    string_type = str


class SQL(DataLayer):
    """
    SQLAlchemy data access layer for Eve REST API.
    """
    driver = db
    serializers = {'datetime': str_to_date}

    def init_app(self, app):
        try:
            # FIXME: dumb double initialisation of the
            # driver because Eve sets it to None in __init__
            self.driver = db
            self.driver.app = app
            self.driver.init_app(app)
        except Exception as e:
            raise ConnectionException(e)

        self.register_schema(app)

    @classmethod
    def lookup_model(cls, model_name):
        """
        Lookup SQLAlchemy model class by its name

        :param model_name: Name of SQLAlchemy model.
        """
        return cls.driver.Model._decl_class_registry[model_name]

#    @classmethod
    def register_schema(self, app, model_name=None):
        """Register eve schema for SQLAlchemy model(s)
        :param app: Flask application instance.
        :param model_name: Name of SQLAlchemy model
            (register all models if not provided)
        """
        if model_name:
            models = {model_name.capitalize(): self.driver.
                      Model._decl_class_registry[model_name.capitalize()]}
        else:
            models = self.driver.Model._decl_class_registry

        for model_name, model_cls in models.items():
            if model_name.startswith('_'):
                continue
            if getattr(model_cls, '_eve_schema', None):
                eve_schema = model_cls._eve_schema
                dict_update(app.config['DOMAIN'], eve_schema)

        for k, v in app.config['DOMAIN'].items():
            # If a resource has a relation, copy the properties of the relation
            if 'datasource' in v and 'source' in v['datasource']:
                source = v['datasource']['source']
                source = app.config['DOMAIN'].get(source.lower())
                if source:
                    v['schema'] = source['schema']
                    v['item_lookup_field'] = source['item_lookup_field']
                    v['item_url'] = source['item_url']

    def find(self, resource, req, sub_resource_lookup):
        """Retrieves a set of documents matching a given request. Queries can
        be expressed in two different formats: the mongo query syntax, and the
        python syntax. The first kind of query would look like: ::

            ?where={"name": "john doe}

        while the second would look like: ::

            ?where=name=="john doe"

        The resultset if paginated.

        :param resource: resource name.
        :param req: a :class:`ParsedRequest`instance.
        :param sub_resource_lookup: sub-resource lookup from the endpoint url.
        """
        args = {'sort': extract_sort_arg(req),
                'resource': resource}

        client_projection = self._client_projection(req)
        client_embedded = self._client_embedded(req)
        model, args['spec'], fields, args['sort'] = \
            self._datasource_ex(resource, [], client_projection,
                                args['sort'], client_embedded)
        if req.where:
            try:
                args['spec'] = self.combine_queries(args['spec'],
                                                    parse(req.where, model))
            except ParseError:
                try:
                    spec = json.loads(req.where)
                    args['spec'] = \
                        self.combine_queries(args['spec'],
                                             parse_dictionary(spec, model))
                except (AttributeError, TypeError):
                    # if parse failed and json loads fails - raise 400
                    abort(400)

        bad_filter = validate_filters(args['spec'], resource)
        if bad_filter:
            abort(400, bad_filter)

        if sub_resource_lookup:
            args['spec'] = \
                self.combine_queries(args['spec'],
                                     parse_dictionary(sub_resource_lookup,
                                                      model))

        if req.if_modified_since:
            updated_filter = sqla_op.gt(getattr(model, config.LAST_UPDATED),
                                        req.if_modified_since)
            args['spec'].append(updated_filter)

        query = self.driver.session.query(model)

        if args['sort']:
            ql = []
            for sort_item in args['sort']:
                ql.append(parse_sorting(model, query, *sort_item))
            args['sort'] = ql

        if req.max_results:
            args['max_results'] = req.max_results
        if req.page > 1:
            args['page'] = req.page
        return SQLAResultCollection(query, fields, **args)

    def find_one(self, resource, req, **lookup):
        client_projection = self._client_projection(req)
        client_embedded = self._client_embedded(req)
        model, filter_, fields, _ = \
            self._datasource_ex(resource, [], client_projection, None,
                                client_embedded)

        if isinstance(lookup.get(config.ID_FIELD), dict) \
                or isinstance(lookup.get(config.ID_FIELD), list):
            # very dummy way to get the related object
            # that commes from embeddable parameter
            return lookup
        else:
            filter_ = self.combine_queries(filter_,
                                           parse_dictionary(lookup, model))
            query = self.driver.session.query(model)
            document = query.filter(*filter_).first()

        return sqla_object_to_dict(document, fields) if document else None

    def find_one_raw(self, resource, _id):
        raise NotImplementedError

    def find_list_of_ids(self, resource, ids, client_projection=None):
        raise NotImplementedError

    def insert(self, resource, doc_or_docs):
        rv = []
        model, filter_, fields_, _ = self._datasource_ex(resource)
        for document in doc_or_docs:
            model_instance = model(**document)
            self.driver.session.add(model_instance)
            self.driver.session.commit()
            id_field = getattr(model_instance, self.driver.app.config['ID_FIELD'])
            document['_id'] = id_field
            rv.append(id_field)
        return rv

    def replace(self, resource, id_, document, original):
        model, filter_, fields_, _ = self._datasource_ex(resource, [])
        id_field = self.driver.app.config['ID_FIELD']
        filter_ = self.combine_queries(filter_,
                                       parse_dictionary({id_field: id_}, model))
        query = self.driver.session.query(model)

        # Find and delete the old object
        old_model_instance = query.filter(*filter_).first()
        if old_model_instance is None:
            abort(500, description=debug_error_message('Object not existent'))
        self.driver.session.delete(old_model_instance)
        self.driver.session.commit()

        # create and insert the new one
        model_instance = model(**document)
        model_instance._id = id_
        self.driver.session.add(model_instance)
        self.driver.session.commit()

    def update(self, resource, id_, updates, original):
        model, filter_, _, _ = self._datasource_ex(resource, [])
        id_field = self.driver.app.config['ID_FIELD']
        filter_ = self.combine_queries(filter_,
                                       parse_dictionary({id_field: id_}, model))
        query = self.driver.session.query(model)
        model_instance = query.filter(*filter_).first()
        if model_instance is None:
            abort(500, description=debug_error_message('Object not existent'))
        for k, v in updates.items():
            setattr(model_instance, k, v)
        self.driver.session.commit()

    def remove(self, resource, lookup):
        model, filter_, _, _ = self._datasource_ex(resource, [])
        filter_ = self.combine_queries(filter_,
                                       parse_dictionary(lookup, model))
        query = self.driver.session.query(model)
        if len(filter_):
            query = query.filter(*filter_)
        for item in query:
            self.driver.session.delete(item)

        self.driver.session.commit()

    @staticmethod
    def _source(resource):
        return config.SOURCES[resource]['source']

    def _model(self, resource):
        return self.lookup_model(self._source(resource))

    def _parse_filter(self, model, filter):
        """
        Convert from Mongo/JSON style filters to SQLAlchemy expressions.
        """
        if filter is None or len(filter) == 0:
            filter = []
        elif isinstance(filter, string_type):
            filter = parse(filter, model)
        elif isinstance(filter, dict):
            filter = parse_dictionary(filter, model)
        elif not isinstance(filter, list):
            filter = []
        return filter

    def datasource(self, resource):
        """
        Overridden from super to return the actual model class of the database
        table instead of the name of it. We also parse the filter coming from
        the schema definition into a SQL compatible filter
        """
        model = self._model(resource)

        filter_ = config.SOURCES[resource]['filter']
        filter_ = self._parse_filter(model, filter_)
        projection_ = copy(config.SOURCES[resource]['projection'])
        sort_ = copy(config.SOURCES[resource]['default_sort'])
        return model, filter_, projection_, sort_

    # NOTE(Gonéri): preserve the _datasource method for compatibiliy with
    # pre 0.6 Eve release (See: commit 87742343fd0362354b9f75c749651f92d6e4a9c8
    # from the Eve repository)
    def _datasource(self, resource):
        return self.datasource(resource)

    def _datasource_ex(self, resource, query=None, client_projection=None,
                       client_sort=None, client_embedded=None):
        model, filter_, fields_, sort_ = \
            super(SQL, self)._datasource_ex(resource, query, client_projection,
                                            client_sort)
        filter_ = self._parse_filter(model, filter_)
        if client_embedded:
            fields_.update(client_embedded)
        fields = [field for field in fields_.keys() if fields_[field]]
        return model, filter_, fields, sort_

    def combine_queries(self, query_a, query_b):
        # TODO: dumb concatenation of query lists.
        #       We really need to check for duplicate queries
        query_a.extend(query_b)
        return query_a

    def is_empty(self, resource):
        model, filter_, _, _ = self.datasource(resource)
        query = self.driver.session.query(model)
        if len(filter_):
            return query.filter_by(*filter_).count() == 0
        else:
            return query.count() == 0

    def _client_embedded(self, req):
        """ Returns a properly parsed client embeddable if available.

        :param req: a :class:`ParsedRequest` instance.

        .. versionadded:: 0.4
        """
        client_embedded = {}
        if req and req.embedded:
            try:
                client_embedded = json.loads(req.embedded)
            except:
                abort(400, description=debug_error_message(
                    'Unable to parse `embedded` clause'
                ))
        return client_embedded

    def _client_projection(self, req):
        """ Returns a properly parsed client projection if available.

        :param req: a :class:`ParsedRequest` instance.

        .. versionadded:: 0.4
        """
        client_projection = {}
        if req and req.projection:
            try:
                client_projection = json.loads(req.projection)
            except:
                abort(400, description=debug_error_message(
                    'Unable to parse `projection` clause'
                ))
        return client_projection
