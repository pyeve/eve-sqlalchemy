# -*- coding: utf-8 -*-
import eve
import string
import random
import os
import copy

from datetime import datetime
from eve import ETAG
from eve.tests import TestMinimal
from eve.utils import date_to_str

from eve_sqlalchemy.tests import test_sql_tables
from eve_sqlalchemy.validation import ValidatorSQL
from eve_sqlalchemy import SQL

EVE = 4


class TestBaseSQL(TestMinimal):

    test_sql_tables = test_sql_tables

    def setUp(self, settings_file=None, url_converters=None):
        self.connection = None
        self.known_resource_count = 101
        self.this_directory = os.path.dirname(os.path.realpath(__file__))
        self.settings_file = os.path.join(self.this_directory,
                                          'test_settings_sql.py')
        self.app = eve.Eve(settings=self.settings_file,
                           url_converters=url_converters,
                           data=SQL,
                           validator=ValidatorSQL)
        self.test_client = self.app.test_client()
        self.app.config = copy.deepcopy(self.app.config)
        self.domain = self.app.config['DOMAIN']
        self.setupDB()

        self.known_resource = 'people'
        self.known_resource_url = \
            ('/%s' % self.domain[self.known_resource]['url'])
        self.unknown_resource = 'unknown'
        self.unknown_resource_url = '/%s' % self.unknown_resource
        self.unknown_item_id = 83542635967
        self.unknown_item_name = 'unknown'
        self.unknown_item_id_url = \
            ('/%s/%s' % (self.domain[self.known_resource]['url'],
                         self.unknown_item_id))
        response, _ = self.get(self.known_resource, '?max_results=2')
        person = self.response_item(response)
        self.item = person
        self.item_id = self.item[self.app.config['ID_FIELD']]
        self.item_firstname = self.item['firstname']
        self.item_etag = self.item[ETAG]
        self.item_id_url = ('/%s/%s' %
                            (self.domain[self.known_resource]['url'],
                             self.item_id))

        self.empty_resource = 'empty'
        self.empty_resource_url = '/%s' % self.empty_resource

        self.different_resource = 'users'
        self.different_resource_url = \
            ('/%s' % self.domain[self.different_resource]['url'])

        response, _ = self.get('users')
        user = self.response_item(response)
        self.user_id = user[self.app.config['ID_FIELD']]
        self.user_firstname = user['firstname']
        self.user_etag = user[ETAG]
        self.user_id_url = ('/%s/%s' %
                            (self.domain[self.different_resource]['url'],
                             self.user_id))
        self.user_firstname_url = \
            ('/%s/%s' % (self.domain[self.different_resource]['url'],
                         self.user_firstname))

        response, _ = self.get('invoices')
        invoice = self.response_item(response)
        self.invoice_id = invoice[self.app.config['ID_FIELD']]
        self.invoice_etag = invoice[ETAG]
        self.invoice_id_url = ('/%s/%s' % (self.domain['invoices']['url'],
                                           self.invoice_id))

        self.readonly_resource = 'payments'
        self.readonly_resource_url = (
            '/%s' % self.domain[self.readonly_resource]['url'])

        response, _ = self.get('payments', '?max_results=1')
        self.readonly_id = self.response_item(response)['_id']
        self.readonly_id_url = ('%s/%s' % (self.readonly_resource_url,
                                           self.readonly_id))

        self.epoch = date_to_str(datetime(1970, 1, 1))

    def setupDB(self):
        self.connection = self.app.data.driver
        self.connection.session.execute('pragma foreign_keys=on')
        self.connection.drop_all()
        self.connection.create_all()
        self.bulk_insert()

    def tearDown(self):
        self.dropDB()
        del self.app

    def dropDB(self):
        self.connection = self.app.data.driver
        self.connection.session.remove()
        self.connection.drop_all()

    def bulk_insert(self):
        sql_tables = self.test_sql_tables
        if not self.connection.session.query(sql_tables.People).count():
            # load random people in db
            people = self.random_people(self.known_resource_count)
            people = [sql_tables.People.from_tuple(item) for item in people]
            for person in people:
                dt = datetime.now()
                person._created = dt
                person._updated = dt
                self.connection.session.add(person)
            self.connection.session.commit()

            # load random invoice
            invoice = sql_tables.Invoices(number=random.randint(0, 100))
            invoice.people_id = people[0]._id
            invoice._created = datetime.now()
            invoice._updated = datetime.now()
            self.connection.session.add(invoice)
            self.connection.session.commit()

            # load random payments
            for _ in range(10):
                payment = sql_tables.Payments(number=random.randint(0, 100),
                                              string=self.random_string(6))
                dt = datetime.now()
                payment._created = dt
                payment._updated = dt
                self.connection.session.add(payment)
            self.connection.session.commit()

    def random_string(self, length=6):
        return ''.join(random.choice(string.ascii_lowercase)
                       for _ in range(length)).capitalize()

    def random_people(self, num):
        people = []
        for i in range(num):
            people.append((self.random_string(6), self.random_string(6), i))
        return people

    def response_item(self, response, i=0):
        if self.app.config['HATEOAS']:
            return response['_items'][i]
        else:
            return response[i]
