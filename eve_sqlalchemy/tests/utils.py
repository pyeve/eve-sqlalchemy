# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

import mock

from eve_sqlalchemy.utils import extract_sort_arg


class TestUtils(unittest.TestCase):

    def test_extract_sort_arg_standard(self):
        req = mock.Mock()
        req.sort = 'created_at,-name'
        self.assertEqual(extract_sort_arg(req), [['created_at'], ['name', -1]])

    def test_extract_sort_arg_sqlalchemy(self):
        req = mock.Mock()
        req.sort = '[("created_at", -1, "nullstart")]'
        self.assertEqual(extract_sort_arg(req),
                         [('created_at', -1, 'nullstart')])

    def test_extract_sort_arg_null(self):
        req = mock.Mock()
        req.sort = ''
        self.assertEqual(extract_sort_arg(req), None)
