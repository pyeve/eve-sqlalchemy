# -*- coding:utf-8 -*-

import unittest

from eve_sqlalchemy import SQL
from eve_sqlalchemy import EveSqlalchemy

from eve_sqlalchemy.validation import ValidatorSQL

from eve_sqlalchemy.tests import SETTINGS_FILE


class FakeAuth:

    def __init__(self, app):
        self.app = app


class TestConstructor(unittest.TestCase):

    def test_constructor(self):
        app = EveSqlalchemy(
            settings=SETTINGS_FILE,
            validator=ValidatorSQL,
            data=SQL,
            auth=FakeAuth,
        )

        assert isinstance(app.auth, FakeAuth)
        assert isinstance(app.auth.app, EveSqlalchemy)
