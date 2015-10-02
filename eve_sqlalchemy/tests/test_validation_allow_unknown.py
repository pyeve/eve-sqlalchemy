# -*- coding: utf-8 -*-

import eve_sqlalchemy.validation
from eve_sqlalchemy.tests.test_settings_sql import DOMAIN
from eve.utils import config

import unittest


class TestValidator(unittest.TestCase):
    def setUp(self):
        schemas = {
            'mock_string': {
                'type': 'string',
            },
        }
        # This is usually set in a users' app
        DOMAIN['people'].update({
            'allow_unknown': True,
        })
        config.DOMAIN = DOMAIN
        self.validator = eve_sqlalchemy.validation.ValidatorSQL(schemas, resource='people')

    def test_allow_unknown_true(self):
        self.assertTrue(self.validator.allow_unknown)
