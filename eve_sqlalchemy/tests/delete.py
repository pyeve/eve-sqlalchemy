# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from eve import ETAG
from eve.tests.methods import delete as eve_delete_tests
from eve.tests.utils import DummyEvent

from eve_sqlalchemy.tests import TestBase


class TestDelete(eve_delete_tests.TestDelete, TestBase):

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_delete_from_resource_endpoint_write_concern(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_delete_write_concern(self):
        pass

    def test_delete_subresource(self):
        # Eve test uses the Mongo layer directly.
        # TODO: Fix directly in Eve and remove this override

        with self.app.app_context():
            # create random contact
            fake_contact = self.random_contacts(1)[0]
            fake_contact['username'] = 'foo'
            fake_contact_id = self.app.data.insert('contacts',
                                                   [fake_contact])[0]

            # grab parent collection count; we will use this later to make sure
            # we didn't delete all the users in the database. We add one extra
            # invoice to make sure that the actual count will never be 1 (which
            # would invalidate the test)
            self.app.data.insert('invoices', [{'inv_number': 1}])

        response, status = self.get('invoices')
        invoices = len(response[self.app.config['ITEMS']])

        with self.app.app_context():
            # update first invoice to reference the new contact
            self.app.data.update('invoices', self.invoice_id,
                                 {'person': fake_contact_id}, None)

        # verify that the only document retrieved is referencing the correct
        # parent document
        response, status = self.get('users/%s/invoices' % fake_contact_id)
        person_id = response[self.app.config['ITEMS']][0]['person']
        self.assertEqual(person_id, fake_contact_id)

        # delete all documents at the sub-resource endpoint
        response, status = self.delete('users/%s/invoices' % fake_contact_id)
        self.assert204(status)

        # verify that the no documents are left at the sub-resource endpoint
        response, status = self.get('users/%s/invoices' % fake_contact_id)
        self.assertEqual(len(response['_items']), 0)

        # verify that other documents in the invoices collection have not neen
        # deleted
        response, status = self.get('invoices')
        self.assertEqual(len(response['_items']), invoices - 1)

    def test_delete_subresource_item(self):
        # Eve test uses the Mongo layer directly.
        # TODO: Fix directly in Eve and remove this override

        with self.app.app_context():
            # create random contact
            fake_contact = self.random_contacts(1)[0]
            fake_contact['username'] = 'foo'
            fake_contact_id = self.app.data.insert('contacts',
                                                   [fake_contact])[0]

            # update first invoice to reference the new contact
            self.app.data.update('invoices', self.invoice_id,
                                 {'person': fake_contact_id}, None)

        # GET all invoices by new contact
        response, status = self.get('users/%s/invoices/%s' %
                                    (fake_contact_id, self.invoice_id))
        etag = response[ETAG]

        headers = [('If-Match', etag)]
        response, status = self.delete('users/%s/invoices/%s' %
                                       (fake_contact_id, self.invoice_id),
                                       headers=headers)
        self.assert204(status)


class TestDeleteEvents(eve_delete_tests.TestDeleteEvents, TestBase):

    def test_on_delete_item(self):
        devent = DummyEvent(self.before_delete)
        self.app.on_delete_item += devent
        self.delete_item()
        self.assertEqual('contacts', devent.called[0])
        id_field = self.domain['contacts']['id_field']
        # Eve test casts devent.called[1][id_field] to string, which may be
        # appropriate for ObjectIds, but not for integer ids.
        # TODO: Fix directly in Eve and remove this override
        self.assertEqual(self.item_id, devent.called[1][id_field])

    def test_on_delete_item_contacts(self):
        devent = DummyEvent(self.before_delete)
        self.app.on_delete_item_contacts += devent
        self.delete_item()
        id_field = self.domain['contacts']['id_field']
        # Eve test casts devent.called[1][id_field] to string, which may be
        # appropriate for ObjectIds, but not for integer ids.
        # TODO: Fix directly in Eve and remove this override
        self.assertEqual(self.item_id, devent.called[0][id_field])

    def test_on_deleted_item(self):
        devent = DummyEvent(self.after_delete)
        self.app.on_deleted_item += devent
        self.delete_item()
        self.assertEqual('contacts', devent.called[0])
        id_field = self.domain['contacts']['id_field']
        # Eve test casts devent.called[1][id_field] to string, which may be
        # appropriate for ObjectIds, but not for integer ids.
        # TODO: Fix directly in Eve and remove this override
        self.assertEqual(self.item_id, devent.called[1][id_field])

    def test_on_deleted_item_contacts(self):
        devent = DummyEvent(self.after_delete)
        self.app.on_deleted_item_contacts += devent
        self.delete_item()
        id_field = self.domain['contacts']['id_field']
        # Eve test casts devent.called[1][id_field] to string, which may be
        # appropriate for ObjectIds, but not for integer ids.
        # TODO: Fix directly in Eve and remove this override
        self.assertEqual(self.item_id, devent.called[0][id_field])

    def before_delete(self):
        # Eve method uses the Mongo layer directly.
        # TODO: Fix directly in Eve and remove this override
        return self.app.data.find_one_raw(
            self.known_resource, self.item_id) is not None
