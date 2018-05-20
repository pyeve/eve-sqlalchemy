# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from eve_sqlalchemy.examples.many_to_one import settings
from eve_sqlalchemy.examples.many_to_one.domain import Base
from eve_sqlalchemy.tests import TestMinimal

SETTINGS = vars(settings)


class TestManyToOne(TestMinimal):

    def setUp(self, url_converters=None):
        super(TestManyToOne, self).setUp(SETTINGS, url_converters, Base)

    def bulk_insert(self):
        self.app.data.insert('children', [{'id': k} for k in range(1, 5)])
        self.app.data.insert('parents', [
            {'id': 1, 'child': 1},
            {'id': 2, 'child': 1},
            {'id': 3}])

    def test_get_related_children_with_where(self):
        response, status = self.get('children', '?where={"parents": 1}')
        self.assert200(status)
        children = response['_items']
        self.assertEqual([c['id'] for c in children], [1])

    def test_get_related_parents_with_where(self):
        response, status = self.get('parents', '?where={"child": 1}')
        self.assert200(status)
        parents = response['_items']
        self.assertEqual([p['id'] for p in parents], [1, 2])
