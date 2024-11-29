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
            'a_media': {
                'type': 'media',
            }
        }
        self.validator = eve_sqlalchemy.validation.ValidatorSQL(schemas)

    def test_type_json(self):
        self.validator.validate_update(
            {'a_json': None}, None)

    def test_type_objectid(self):
        self.validator.validate_update(
            {'a_objectid': ''}, None)

    def test_type_media(self):
        from werkzeug.datastructures import FileStorage

        self.assertFalse(self.validator.validate(
            {'a_media': 100}    # check if integer type data passes through
        ))
        self.assertTrue(self.validator.validate(
            {'a_media': FileStorage(filename=__file__)}
        ))
