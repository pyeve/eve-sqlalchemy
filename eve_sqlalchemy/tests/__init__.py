# -*- coding: utf-8 -*-
"""Base classes for Eve-SQLAlchemy tests.

We try to mimic Eve tests as closely as possible. Therefore we introduce
derived classes for testing of HTTP methods (get, post, put, patch, delete).
Those run the same integration tests as are run for Eve, with some
modifications here and there if the Eve counterparts don't work for us. For
each overridden method there is a comment stating the changes made to the
original Eve test code.
"""
from __future__ import unicode_literals

import collections
import os
import random

import eve
import eve.tests
from eve import ISSUES

from eve_sqlalchemy import SQL
from eve_sqlalchemy.tests.test_sql_tables import Base
from eve_sqlalchemy.validation import ValidatorSQL


class TestMinimal(eve.tests.TestMinimal):

    def setUp(self, settings_file=None, url_converters=None,
              declarative_base=None):
        """ Prepare the test fixture

        :param settings_file: the name of the settings file.  Defaults
                              to `eve/tests/test_settings.py`.

        This is mostly the same as in eve.tests.__init__.py, except the
        creation of self.app.
        """
        self.this_directory = os.path.dirname(os.path.realpath(__file__))
        if settings_file is None:
            # Load the settings file, using a robust path
            settings_file = os.path.join(self.this_directory,
                                         'test_settings.py')

        self.known_resource_count = 101

        self.settings_file = settings_file
        if declarative_base is not None:
            SQL.driver.Model = declarative_base
        else:
            SQL.driver.Model = Base

        self.app = eve.Eve(settings=self.settings_file,
                           url_converters=url_converters, data=SQL,
                           validator=ValidatorSQL)
        self.setupDB()

        self.test_client = self.app.test_client()

        self.domain = self.app.config['DOMAIN']

    def setupDB(self):
        self.connection = self.app.data.driver
        self.connection.session.execute('pragma foreign_keys=on')
        self.connection.drop_all()
        self.connection.create_all()
        self.bulk_insert()

    def dropDB(self):
        self.connection.session.remove()
        self.connection.drop_all()

    def assertValidationError(self, response, matches):
        self.assertTrue(eve.STATUS in response)
        self.assertTrue(eve.STATUS_ERR in response[eve.STATUS])
        self.assertTrue(ISSUES in response)
        issues = response[ISSUES]
        self.assertTrue(len(issues))

        for k, v in matches.items():
            self.assertTrue(k in issues)
            if isinstance(issues[k], collections.Sequence):
                self.assertTrue(v in issues[k])
            if isinstance(issues[k], collections.Mapping):
                self.assertTrue(v in issues[k].values())


class TestBase(eve.tests.TestBase, TestMinimal):

    def setUp(self, url_converters=None):
        super(TestBase, self).setUp(url_converters)
        self.unknown_item_id = 424242
        self.unknown_item_id_url = ('/%s/%s' %
                                    (self.domain[self.known_resource]['url'],
                                     self.unknown_item_id))

    def random_contacts(self, num, standard_date_fields=True):
        contacts = \
            super(TestBase, self).random_contacts(num, standard_date_fields)
        return [self._create_contact_dict(dict_) for dict_ in contacts]

    def _create_contact_dict(self, dict_):
        result = self._filter_keys_by_schema(dict_, 'contacts')
        result['tid'] = random.randint(1, 10000)
        if 'username' not in dict_ or dict_['username'] is None:
            result['username'] = ''
        return result

    def _filter_keys_by_schema(self, dict_, resource):
        allowed_keys = self.app.config['DOMAIN'][resource]['schema'].keys()
        keys = set(dict_.keys()) & set(allowed_keys)
        return dict([(key, dict_[key]) for key in keys])

    def random_payments(self, num):
        payments = super(TestBase, self).random_payments(num)
        return [self._filter_keys_by_schema(dict_, 'payments')
                for dict_ in payments]

    def random_invoices(self, num):
        invoices = super(TestBase, self).random_invoices(num)
        return [self._filter_keys_by_schema(dict_, 'invoices')
                for dict_ in invoices]

    def random_internal_transactions(self, num):
        transactions = super(TestBase, self).random_internal_transactions(num)
        return [self._filter_keys_by_schema(dict_, 'internal_transactions')
                for dict_ in transactions]

    def random_products(self, num):
        products = super(TestBase, self).random_products(num)
        return [self._filter_keys_by_schema(dict_, 'products')
                for dict_ in products]

    def bulk_insert(self):
        self.app.data.insert('contacts',
                             self.random_contacts(self.known_resource_count))
        self.app.data.insert('users', self.random_users(2))
        self.app.data.insert('payments', self.random_payments(10))
        self.app.data.insert('invoices', self.random_invoices(1))
        self.app.data.insert('internal_transactions',
                             self.random_internal_transactions(4))
        self.app.data.insert('products', self.random_products(2))
