# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from eve import ETAG
from eve.tests.methods import patch as eve_patch_tests

from eve_sqlalchemy.tests import TestBase


class TestPatch(eve_patch_tests.TestPatch, TestBase):

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_patch_objectid(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_patch_null_objectid(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_patch_defaults(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_patch_defaults_with_post_override(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_patch_write_concern_fail(self):
        pass

    def test_patch_missing_standard_date_fields(self):
        # Eve test uses the Mongo layer directly.
        # TODO: Fix directly in Eve and remove this override

        with self.app.app_context():
            contacts = self.random_contacts(1, False)
            ref = 'test_patch_missing_date_f'
            contacts[0]['ref'] = ref
            self.app.data.insert('contacts', contacts)

        # now retrieve same document via API and get its etag, which is
        # supposed to be computed on default DATE_CREATED and LAST_UPDATAED
        # values.
        response, status = self.get(self.known_resource, item=ref)
        etag = response[ETAG]
        _id = response['_id']

        # attempt a PATCH with the new etag.
        field = "ref"
        test_value = "X234567890123456789012345"
        changes = {field: test_value}
        _, status = self.patch('%s/%s' % (self.known_resource_url, _id),
                               data=changes, headers=[('If-Match', etag)])
        self.assert200(status)

    def test_patch_subresource(self):
        # Eve test uses the Mongo layer directly.
        # TODO: Fix directly in Eve and remove this override

        with self.app.app_context():
            # create random contact
            fake_contact = self.random_contacts(1)
            fake_contact_id = self.app.data.insert('contacts', fake_contact)[0]

            # update first invoice to reference the new contact
            self.app.data.update('invoices', self.invoice_id,
                                 {'person': fake_contact_id}, None)

        # GET all invoices by new contact
        response, status = self.get('users/%s/invoices/%s' %
                                    (fake_contact_id, self.invoice_id))
        etag = response[ETAG]

        data = {"inv_number": "new_number"}
        headers = [('If-Match', etag)]
        response, status = self.patch('users/%s/invoices/%s' %
                                      (fake_contact_id, self.invoice_id),
                                      data=data, headers=headers)
        self.assert200(status)
        self.assertPatchResponse(response, self.invoice_id, 'peopleinvoices')

    @pytest.mark.xfail(True, run=False, reason='not implemented yet')
    def test_patch_nested_document_not_overwritten(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not implemented yet')
    def test_patch_nested_document_nullable_missing(self):
        pass

    def test_patch_dependent_field_on_origin_document(self):
        """ Test that when patching a field which is dependent on another and
        this other field is not provided with the patch but is still present
        on the target document, the patch will be accepted. See #363.
        """
        # Eve remove the default-setting on 'dependency_field1', which we
        # cannot do easily with SQLAlchemy.
        # TODO: Fix directly in Eve and remove this override.

        # this will fail as dependent field is missing even in the
        # document we are trying to update.
        schema = self.domain['contacts']['schema']
        schema['dependency_field2']['dependencies'] = \
            ['dependency_field1_without_default']
        changes = {'dependency_field2': 'value'}
        r, status = self.patch(self.item_id_url, data=changes,
                               headers=[('If-Match', self.item_etag)])
        self.assert422(status)

        # update the stored document by adding dependency field.
        changes = {'dependency_field1_without_default': 'value'}
        r, status = self.patch(self.item_id_url, data=changes,
                               headers=[('If-Match', self.item_etag)])
        self.assert200(status)

        # now the field2 update will be accepted as the dependency field is
        # present in the stored document already.
        etag = r['_etag']
        changes = {'dependency_field2': 'value'}
        r, status = self.patch(self.item_id_url, data=changes,
                               headers=[('If-Match', etag)])
        self.assert200(status)

    def test_id_field_in_document_fails(self):
        # Eve test uses ObjectId as id.
        self.app.config['IF_MATCH'] = False
        id_field = self.domain[self.known_resource]['id_field']
        data = {id_field: 424242}
        r, status = self.patch(self.item_id_url, data=data)
        self.assert400(status)
        self.assertTrue('immutable' in r['_error']['message'])


class TestEvents(eve_patch_tests.TestEvents, TestBase):

    def before_update(self):
        # Eve test code uses mongo layer directly.
        # TODO: Fix directly in Eve and remove this override
        contact = self.app.data.find_one_raw(self.known_resource, self.item_id)
        return contact['ref'] == self.item_name
