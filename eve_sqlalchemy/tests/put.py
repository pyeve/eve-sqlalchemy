# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
import six
from eve import ETAG, STATUS
from eve.tests.methods import put as eve_put_tests

from eve_sqlalchemy.tests import TestBase


class TestPut(eve_put_tests.TestPut, TestBase):

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_put_dbref_subresource(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_allow_unknown(self):
        pass

    def test_put_x_www_form_urlencoded_number_serialization(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.
        field = 'anumber'
        test_value = 41
        changes = {field: test_value,
                   'ref': 'test_put_x_www_num_ser_12'}
        headers = [('If-Match', self.item_etag)]
        r, status = self.parse_response(self.test_client.put(
            self.item_id_url, data=changes, headers=headers))
        self.assert200(status)
        self.assertTrue('OK' in r[STATUS])

    def test_put_referential_integrity_list(self):
        data = {"invoicing_contacts": [self.item_id, self.unknown_item_id]}
        headers = [('If-Match', self.invoice_etag)]
        r, status = self.put(self.invoice_id_url, data=data, headers=headers)
        self.assertValidationErrorStatus(status)
        expected = ("value '%s' must exist in resource '%s', field '%s'" %
                    (self.unknown_item_id, 'contacts',
                     self.domain['contacts']['id_field']))
        self.assertValidationError(r, {'invoicing_contacts': expected})

        # Eve test posts a list with self.item_id twice, which can't be handled
        # for our case because we use (invoice_id, contact_id) as primary key
        # in the association table.
        data = {"invoicing_contacts": [self.item_id]}
        r, status = self.put(self.invoice_id_url, data=data, headers=headers)
        self.assert200(status)
        self.assertPutResponse(r, self.invoice_id, 'invoices')

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_put_write_concern_fail(self):
        pass

    def test_put_subresource(self):
        # Eve test uses mongo layer directly.
        self.app.config['BANDWIDTH_SAVER'] = False

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
        response, status = self.put('users/%s/invoices/%s' %
                                    (fake_contact_id, self.invoice_id),
                                    data=data, headers=headers)
        self.assert200(status)
        self.assertPutResponse(response, self.invoice_id, 'peopleinvoices')
        self.assertEqual(response.get('person'), fake_contact_id)

    def test_put_dependency_fields_with_default(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.
        field = "dependency_field2"
        test_value = "a value"
        changes = {field: test_value,
                   'ref': 'test_post_dep_with_def_12'}
        r = self.perform_put(changes)
        db_value = self.compare_put_with_get(field, r)
        self.assertEqual(db_value, test_value)

    def test_put_dependency_fields_with_wrong_value(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.
        r, status = self.put(self.item_id_url,
                             data={'dependency_field3': 'value',
                                   'ref': 'test_post_dep_wrong_fiel1'},
                             headers=[('If-Match', self.item_etag)])
        self.assert422(status)
        r, status = self.put(self.item_id_url,
                             data={'dependency_field1': 'value',
                                   'dependency_field3': 'value',
                                   'ref': 'test_post_dep_wrong_fiel2'},
                             headers=[('If-Match', self.item_etag)])
        self.assert200(status)

    def test_put_creates_unexisting_document(self):
        # Eve test uses ObjectId as id.
        id = 424242
        url = '%s/%s' % (self.known_resource_url, id)
        id_field = self.domain[self.known_resource]['id_field']
        changes = {"ref": "1234567890123456789012345"}
        r, status = self.put(url, data=changes)
        # 201 is a creation (POST) response
        self.assert201(status)
        # new document has id_field matching the PUT endpoint
        self.assertEqual(r[id_field], id)

    def test_put_returns_404_on_unexisting_document(self):
        # Eve test uses ObjectId as id.
        self.app.config['UPSERT_ON_PUT'] = False
        id = 424242
        url = '%s/%s' % (self.known_resource_url, id)
        changes = {"ref": "1234567890123456789012345"}
        r, status = self.put(url, data=changes)
        self.assert404(status)

    def test_put_creates_unexisting_document_with_url_as_id(self):
        # Eve test uses ObjectId as id.
        id = 424242
        url = '%s/%s' % (self.known_resource_url, id)
        id_field = self.domain[self.known_resource]['id_field']
        changes = {"ref": "1234567890123456789012345",
                   id_field: 848484}  # mismatching id
        r, status = self.put(url, data=changes)
        # 201 is a creation (POST) response
        self.assert201(status)
        # new document has id_field matching the PUT endpoint
        # (eventual mismatching id_field in the payload is ignored/replaced)
        self.assertEqual(r[id_field], id)

    def test_put_creates_unexisting_document_fails_on_mismatching_id(self):
        # Eve test uses ObjectId as id.
        id = 424243
        id_field = self.domain[self.known_resource]['id_field']
        changes = {"ref": "1234567890123456789012345", id_field: id}
        r, status = self.put(self.item_id_url,
                             data=changes,
                             headers=[('If-Match', self.item_etag)])
        self.assert400(status)
        self.assertTrue('immutable' in r['_error']['message'])

    def compare_put_with_get(self, fields, put_response):
        # Eve methods checks for instance of str, which could be unicode for
        # Python 2. We use six.string_types instead.
        raw_r = self.test_client.get(self.item_id_url)
        r, status = self.parse_response(raw_r)
        self.assert200(status)
        # Since v0.7, ETag conform to RFC 7232-2.3 (see Eve#794)
        self.assertEqual(raw_r.headers.get('ETag')[1:-1],
                         put_response[ETAG])
        if isinstance(fields, six.string_types):
            return r[fields]
        else:
            return [r[field] for field in fields]


class TestEvents(eve_put_tests.TestEvents, TestBase):

    def before_replace(self):
        # Eve test code uses mongo layer directly.
        # TODO: Fix directly in Eve and remove this override
        contact = self.app.data.find_one_raw(self.known_resource, self.item_id)
        return contact['ref'] == self.item_name
