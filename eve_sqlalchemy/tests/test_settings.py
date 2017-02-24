# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy

# db_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),
#                            'test.db')
SQLALCHEMY_DATABASE_URI = 'sqlite:///'  # %s' % db_filename

# SQLALCHEMY_ECHO = True
# SQLALCHEMY_RECORD_QUERIES = True

SERVER_NAME = 'localhost:5000'

ID_FIELD = '_id'
ITEM_LOOKUP = True
ITEM_LOOKUP_FIELD = ID_FIELD

RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PATCH', 'DELETE', 'PUT']

disabled_bulk = {
    'url': 'somebulkurl',
    'item_title': 'bulkdisabled',
    'bulk_enabled': False
}

contacts = {
    'url': 'arbitraryurl',
    'cache_control': 'max-age=20,must-revalidate',
    'cache_expires': 20,
    'item_title': 'contact',
    'additional_lookup': {
        'url': 'regex("[\w]+")',
        'field': 'ref'
    },
    'datasource': {'filter': 'username == ""'},
    'schema': {
        'ref': {
            'minlength': 25
        },
        'role': {
            'type': 'list',
            'allowed': ["agent", "client", "vendor"],
        },
        'rows': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    'sku': {'type': 'string', 'maxlength': 10},
                    'price': {'type': 'integer'},
                },
            },
        },
        'alist': {
            'type': 'list',
            'items': [{'type': 'string'}, {'type': 'integer'}, ]
        },
        'location': {
            'type': 'dict',
            'schema': {
                'address': {'type': 'string'},
                'city': {'type': 'string', 'required': True}
            },
        },
        'dependency_field2': {
            'dependencies': ['dependency_field1']
        },
        'dependency_field3': {
            'dependencies': {'dependency_field1': 'value'}
        },
        'read_only_field': {
            'readonly': True
        },
        'propertyschema_dict': {
            'type': 'dict',
            'propertyschema': {'type': 'string', 'regex': '[a-z]+'}
        },
        'valueschema_dict': {
            'type': 'dict',
            'valueschema': {'type': 'integer'}
        },
        'anumber': {
            'type': 'number'
        }
    }
}

companies = {
    'schema': {
        'departments': {
            'type': 'list',
            'schema': {
                'type': 'integer',
                'data_relation': {'resource': 'departments', 'field': '_id'},
                'required': False
            }
        }
    }
}
departments = {
    'internal_resource': True,
}

users = copy.deepcopy(contacts)
users['url'] = 'users'
users['datasource'] = {'source': 'Contacts',
                       'projection': {'username': 1, 'ref': 1},
                       'filter': 'username != ""'}
users['resource_methods'] = ['DELETE', 'POST', 'GET']
users['item_title'] = 'user'
users['additional_lookup']['field'] = 'username'

users_overseas = copy.deepcopy(users)
users_overseas['url'] = 'users/overseas'
users_overseas['datasource'] = {'source': 'Contacts'}

invoices = {}
empty = {}

required_invoices = {
    'schema': {
        'person': {
            'required': True
        }
    }
}

users_invoices = copy.deepcopy(invoices)
users_invoices['url'] = 'users/<regex("[0-9]+"):person>/invoices'
users_invoices['datasource'] = {'source': 'Invoices'}

users_required_invoices = copy.deepcopy(invoices)
users_required_invoices['url'] = \
    'users/<regex("[0-9]+"):person>/required_invoices'
users_required_invoices['datasource'] = {'source': 'Invoices'}
users_required_invoices['schema'] = {
    'person': {
        'required': True
    }
}

payments = {
    'resource_methods': ['GET'],
    'item_methods': ['GET'],
}

internal_transactions = {
    'resource_methods': ['GET'],
    'item_methods': ['GET'],
    'internal_resource': True
}

login = {
    'datasource': {
        'projection': {
            'password': 0
        }
    }
}

products = {
    'id_field': 'sku',
    'item_lookup_field': 'sku',
    'item_url': 'regex("[A-Z]+")'
}
child_products = copy.deepcopy(products)
child_products['url'] = \
    'products/<regex("[A-Z]+"):parent_product_sku>/children'
child_products['datasource'] = {'source': 'Products'}

DOMAIN = {
    'disabled_bulk': disabled_bulk,
    'contacts': contacts,
    'users': users,
    'users_overseas': users_overseas,
    'invoices': invoices,
    # 'versioned_invoices': versioned_invoices,
    'required_invoices': required_invoices,
    'payments': payments,
    'empty': empty,
    # 'restricted': user_restricted_access,
    'peopleinvoices': users_invoices,
    'peoplerequiredinvoices': users_required_invoices,
    # 'peoplesearches': users_searches,
    'companies': companies,
    'departments': departments,
    'internal_transactions': internal_transactions,
    # 'ids': ids,
    'login': login,
    'products': products,
    'child_products': child_products,
}
