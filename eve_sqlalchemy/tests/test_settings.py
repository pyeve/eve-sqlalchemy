# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy

from eve_sqlalchemy.config import DomainConfig, ResourceConfig
from eve_sqlalchemy.tests.test_sql_tables import (
    Contacts, DisabledBulk, Empty, InternalTransactions, Invoices, Login,
    Payments, Products,
)

SQLALCHEMY_DATABASE_URI = 'sqlite:///'  # %s' % db_filename
SQLALCHEMY_TRACK_MODIFICATIONS = False

RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PATCH', 'DELETE', 'PUT']

DOMAIN = DomainConfig({
    'disabled_bulk': ResourceConfig(DisabledBulk),
    'contacts': ResourceConfig(Contacts),
    'invoices': ResourceConfig(Invoices),
    # 'versioned_invoices': versioned_invoices,
    'payments': ResourceConfig(Payments),
    'empty': ResourceConfig(Empty),
    # 'restricted': user_restricted_access,
    # 'peoplesearches': users_searches,
    # 'companies': ResourceConfig(Companies),
    # 'departments': ResourceConfig(Departments),
    'internal_transactions': ResourceConfig(InternalTransactions),
    # 'ids': ids,
    'login': ResourceConfig(Login),
    'products': ResourceConfig(Products, id_field='sku')
}).render()

DOMAIN['disabled_bulk'].update({
    'url': 'somebulkurl',
    'item_title': 'bulkdisabled',
    'bulk_enabled': False
})

DOMAIN['contacts'].update({
    'url': 'arbitraryurl',
    'cache_control': 'max-age=20,must-revalidate',
    'cache_expires': 20,
    'item_title': 'contact',
    'additional_lookup': {
        'url': r'regex("[\w]+")',
        'field': 'ref'
    }
})
DOMAIN['contacts']['datasource']['filter'] = 'username == ""'
DOMAIN['contacts']['schema']['ref']['minlength'] = 25
DOMAIN['contacts']['schema']['role'].update({
    'type': 'list',
    'allowed': ["agent", "client", "vendor"],
})
DOMAIN['contacts']['schema']['rows'].update({
    'type': 'list',
    'schema': {
        'type': 'dict',
        'schema': {
            'sku': {'type': 'string', 'maxlength': 10},
            'price': {'type': 'integer'},
        },
    },
})
DOMAIN['contacts']['schema']['alist'].update({
    'type': 'list',
    'items': [{'type': 'string'}, {'type': 'integer'}, ]
})
DOMAIN['contacts']['schema']['location'].update({
    'type': 'dict',
    'schema': {
        'address': {'type': 'string'},
        'city': {'type': 'string', 'required': True}
    },
})
DOMAIN['contacts']['schema']['dependency_field2'].update({
    'dependencies': ['dependency_field1']
})
DOMAIN['contacts']['schema']['dependency_field3'].update({
    'dependencies': {'dependency_field1': 'value'}
})
DOMAIN['contacts']['schema']['read_only_field'].update({
    'readonly': True
})
DOMAIN['contacts']['schema']['propertyschema_dict'].update({
    'type': 'dict',
    'propertyschema': {'type': 'string', 'regex': '[a-z]+'}
})
DOMAIN['contacts']['schema']['valueschema_dict'].update({
    'type': 'dict',
    'valueschema': {'type': 'integer'}
})
DOMAIN['contacts']['schema']['anumber'].update({
    'type': 'number'
})

# DOMAIN['companies']['schema']['departments'].update({
#     'type': 'list',
#     'schema': {
#         'type': 'integer',
#         'data_relation': {'resource': 'departments', 'field': '_id'},
#         'required': False
#     }
# })
# DOMAIN['departments'].update({
#     'internal_resource': True,
# })

users = copy.deepcopy(DOMAIN['contacts'])
users['url'] = 'users'
users['datasource'] = {'source': 'Contacts',
                       'projection': {'username': 1, 'ref': 1},
                       'filter': 'username != ""'}
users['resource_methods'] = ['DELETE', 'POST', 'GET']
users['item_title'] = 'user'
users['additional_lookup']['field'] = 'username'
DOMAIN['users'] = users

users_overseas = copy.deepcopy(DOMAIN['contacts'])
users_overseas['url'] = 'users/overseas'
users_overseas['datasource'] = {'source': 'Contacts'}
DOMAIN['users_overseas'] = users_overseas

required_invoices = copy.deepcopy(DOMAIN['invoices'])
required_invoices['schema']['person'].update({
    'required': True
})
DOMAIN['required_invoices'] = required_invoices

users_invoices = copy.deepcopy(DOMAIN['invoices'])
users_invoices['url'] = 'users/<regex("[0-9]+"):person>/invoices'
users_invoices['datasource'] = {'source': 'Invoices'}
DOMAIN['peopleinvoices'] = users_invoices

users_required_invoices = copy.deepcopy(required_invoices)
users_required_invoices['url'] = \
    'users/<regex("[0-9]+"):person>/required_invoices'
DOMAIN['peoplerequiredinvoices'] = users_required_invoices

DOMAIN['payments'].update({
    'resource_methods': ['GET'],
    'item_methods': ['GET'],
})

DOMAIN['internal_transactions'].update({
    'resource_methods': ['GET'],
    'item_methods': ['GET'],
    'internal_resource': True
})

DOMAIN['login']['datasource']['projection'].update({
    'password': 0
})

child_products = copy.deepcopy(DOMAIN['products'])
child_products['url'] = \
    'products/<regex("[A-Z]+"):parent_product_sku>/children'
child_products['datasource'] = {'source': 'Products'}
DOMAIN['child_products'] = child_products
