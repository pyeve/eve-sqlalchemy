# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

import eve_sqlalchemy.validation


class TestValidator(unittest.TestCase):
    def setUp(self):
        schemas = {
            'a_json': {
                'type': 'json',
            },
            'a_objectid': {
                'type': 'objectid',
            },
        }
        self.validator = eve_sqlalchemy.validation.ValidatorSQL(schemas)

    def test_type_json(self):
        self.validator.validate_update(
            {'a_json': None}, None)

    def test_type_objectid(self):
        self.validator.validate_update(
            {'a_objectid': ''}, None)
