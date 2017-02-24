# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

from eve.utils import config

import eve_sqlalchemy.validation
from eve_sqlalchemy.tests.test_settings import DOMAIN


class TestValidator(unittest.TestCase):
    def setUp(self):
        schemas = {
            'mock_string': {
                'type': 'string',
            },
        }
        # This is usually set in a users' app
        DOMAIN['contacts'].update({
            'allow_unknown': True,
        })
        config.DOMAIN = DOMAIN
        self.validator = eve_sqlalchemy.validation.ValidatorSQL(
            schemas, resource='contacts')

    def test_allow_unknown_true(self):
        self.assertTrue(self.validator.allow_unknown)
