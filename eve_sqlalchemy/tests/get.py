# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

import pytest
import simplejson as json
from eve.tests.methods import get as eve_get_tests

from eve_sqlalchemy.tests import TestBase


class TestGet(eve_get_tests.TestGet, TestBase):

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_get_aggregation_parsing(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_get_aggregation_pagination(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_get_aggregation_endpoint(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_get_where_mongo_combined_date(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_get_mongo_query_blacklist(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_get_where_mongo_objectid_as_string(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not implemented yet')
    def test_get_projection_subdocument(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not implemented yet')
    def test_get_where_disabled(self):
        pass

    def test_documents_missing_standard_date_fields(self):
        """Documents created outside the API context could be lacking the
        LAST_UPDATED and/or DATE_CREATED fields.
        """
        # Eve test uses the Mongo layer directly.
        # TODO: Fix directly in Eve and remove this override
        with self.app.app_context():
            contacts = self.random_contacts(1, False)
            ref = 'test_update_field'
            contacts[0]['ref'] = ref
            self.app.data.insert('contacts', contacts)

        where = '{"ref": "%s"}' % ref
        response, status = self.get(self.known_resource,
                                    '?where=%s' % where)
        self.assert200(status)
        resource = response['_items']
        self.assertEqual(len(resource), 1)
        self.assertItem(resource[0], self.known_resource)

    @pytest.mark.xfail(True, run=False, reason='not implemented yet')
    def test_get_where_allowed_filters(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not implemented yet')
    def test_get_embedded_media(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not implemented yet')
    def test_get_embedded_media_validate_rest_of_fields(self):
        pass

    def test_get_embedded(self):
        # Eve test uses the Mongo layer directly.
        # TODO: Fix directly in Eve and remove this override

        with self.app.app_context():
            # We need to assign a `person` to our test invoice
            fake_contact = self.random_contacts(1)[0]
            fake_contact_id = self.app.data.insert('contacts',
                                                   [fake_contact])[0]
            self.app.data.update('invoices', self.invoice_id,
                                 {'person': fake_contact_id}, None)

        invoices = self.domain['invoices']

        # Test that we get 400 if can't parse dict
        embedded = 'not-a-dict'
        r = self.test_client.get('%s/%s' % (invoices['url'],
                                            '?embedded=%s' % embedded))
        self.assert400(r.status_code)

        # Test that doesn't come embedded if asking for a field that
        # isn't embedded (global setting is False by default)
        embedded = '{"person": 1}'
        r = self.test_client.get('%s/%s' % (invoices['url'],
                                            '?embedded=%s' % embedded))
        self.assert200(r.status_code)
        content = json.loads(r.get_data())
        self.assertEqual(content['_items'][0]['person'], fake_contact_id)

        # Set field to be embedded
        invoices['schema']['person']['data_relation']['embeddable'] = True

        # Test that global setting applies even if field is set to embedded
        invoices['embedding'] = False
        r = self.test_client.get('%s/%s' % (invoices['url'],
                                            '?embedded=%s' % embedded))
        self.assert200(r.status_code)
        content = json.loads(r.get_data())
        self.assertEqual(content['_items'][0]['person'], fake_contact_id)

        # Test that it works
        invoices['embedding'] = True
        r = self.test_client.get('%s/%s' % (invoices['url'],
                                            '?embedded=%s' % embedded))
        self.assert200(r.status_code)
        content = json.loads(r.get_data())
        self.assertTrue('location' in content['_items'][0]['person'])

        # Test that it ignores a bogus field
        embedded = '{"person": 1, "not-a-real-field": 1}'
        r = self.test_client.get('%s/%s' % (invoices['url'],
                                            '?embedded=%s' % embedded))
        self.assert200(r.status_code)
        content = json.loads(r.get_data())
        self.assertTrue('location' in content['_items'][0]['person'])

        # Test that it ignores a real field with a bogus value
        embedded = '{"person": 1, "inv_number": "not-a-real-value"}'
        r = self.test_client.get('%s/%s' % (invoices['url'],
                                            '?embedded=%s' % embedded))
        self.assert200(r.status_code)
        content = json.loads(r.get_data())
        self.assertTrue('location' in content['_items'][0]['person'])

        # Test that it works with item endpoint too
        r = self.test_client.get('%s/%s/%s' % (invoices['url'],
                                               self.invoice_id,
                                               '?embedded=%s' % embedded))
        self.assert200(r.status_code)
        content = json.loads(r.get_data())
        self.assertTrue('location' in content['person'])

        # Add new embeddable field to schema
        invoices['schema']['missing-field'] = {
            'type': 'objectid',
            'data_relation': {'resource': 'contacts', 'embeddable': True}
        }

        # Test that it ignores embeddable field that is missing from document
        embedded = '{"missing-field": 1}'
        r = self.test_client.get('%s/%s' % (invoices['url'],
                                            '?embedded=%s' % embedded))
        self.assert200(r.status_code)
        content = json.loads(r.get_data())
        self.assertFalse('missing-field' in content['_items'][0])

        # Test default fields to be embedded
        invoices['embedded_fields'] = ['person']
        r = self.test_client.get("%s/" % invoices['url'])
        self.assert200(r.status_code)
        content = json.loads(r.get_data())
        self.assertTrue('location' in content['_items'][0]['person'])

        # Test that default fields are overwritten by ?embedded=...0
        embedded = '{"person": 0}'
        r = self.test_client.get("%s/%s" % (invoices['url'],
                                            '?embedded=%s' % embedded))
        self.assert200(r.status_code)
        content = json.loads(r.get_data())
        self.assertTrue(content['_items'][0]['person'], fake_contact_id)

    def test_get_custom_embedded(self):
        # Eve test uses the Mongo layer directly.
        # TODO: Fix directly in Eve and remove this override
        self.app.config['QUERY_EMBEDDED'] = 'included'

        with self.app.app_context():
            # We need to assign a `person` to our test invoice
            fake_contact = self.random_contacts(1)[0]
            fake_contact_id = self.app.data.insert('contacts',
                                                   [fake_contact])[0]
            self.app.data.update('invoices', self.invoice_id,
                                 {'person_id': fake_contact_id}, None)

        invoices = self.domain['invoices']
        invoices['schema']['person']['data_relation']['embeddable'] = True

        # Test that doesn't come embedded if asking for a field that
        # isn't embedded (global setting is False by default)
        embedded = '{"person": 1}'
        invoices['embedding'] = True
        r = self.test_client.get('%s/%s' % (invoices['url'],
                                            '?included=%s' % embedded))
        self.assert200(r.status_code)
        content = json.loads(r.get_data())
        self.assertTrue('location' in content['_items'][0]['person'])

    @pytest.mark.xfail(True, run=False, reason='not implemented yet')
    def test_get_reference_embedded_in_subdocuments(self):
        pass

    def test_get_subresource(self):
        # Eve test uses the Mongo layer directly.
        # TODO: Fix directly in Eve and remove this override

        with self.app.app_context():
            # create random contact
            fake_contact = self.random_contacts(1)[0]
            fake_contact_id = self.app.data.insert('contacts',
                                                   [fake_contact])[0]
            # update first invoice to reference the new contact
            self.app.data.update('invoices', self.invoice_id,
                                 {'person': fake_contact_id}, None)

        # GET all invoices by new contact
        response, status = self.get('users/%s/invoices' % fake_contact_id)
        self.assert200(status)
        # only 1 invoice
        self.assertEqual(len(response['_items']), 1)
        self.assertEqual(len(response['_links']), 2)
        # which links to the right contact
        self.assertEqual(response['_items'][0]['person'], fake_contact_id)

    @pytest.mark.xfail(True, run=False, reason='not implemented yet')
    def test_get_allowed_filters_operators(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not implemented yet')
    def test_get_nested_filter_operators_unvalidated(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not implemented yet')
    def test_get_nested_filter_operators_validated(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not implemented yet')
    def test_get_invalid_where_fields(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_get_lookup_field_as_string(self):
        pass

    def test_get_subresource_with_custom_idfield(self):
        # Eve test uses the Mongo layer directly.
        # TODO: Fix directly in Eve and remove this override
        response, _ = self.get('products')
        parent_product_sku = response['_items'][0]['sku']
        product = {
            'sku': 'BAZ',
            'title': 'Child product',
            'parent_product': parent_product_sku
        }
        self.app.data.insert('products', [product])
        response, status = self.get('products/%s/children' %
                                    parent_product_sku)
        self.assert200(status)
        self.assertEqual(len(response['_items']), 1)
        self.assertEqual(len(response['_links']), 2)
        self.assertEqual(response['_items'][0]['parent_product'],
                         parent_product_sku)

    def test_get_where_sqlalchemy_relation(self):
        # get random contact
        response, status = self.get('contacts', '?max_results=1')
        contact_id = response['_items'][0]['_id']

        with self.app.app_context():
            # create random invoice to reference the contact
            fake_invoice = self.random_invoices(1)[0]
            fake_invoice['person'] = contact_id
            self.app.data.insert('invoices', [fake_invoice])

        # test dict syntax
        response, status = self.get('invoices',
                                    '?where={"person": %d}' % contact_id)
        self.assert200(status)
        self.assertEqual(len(response['_items']), 1)
        self.assertEqual(response['_items'][0]['person'], contact_id)
        # test pythonic syntax
        response, status = self.get('invoices',
                                    '?where=person==%d' % contact_id)
        self.assert200(status)
        self.assertEqual(len(response['_items']), 1)
        self.assertEqual(response['_items'][0]['person'], contact_id)


class TestGetItem(eve_get_tests.TestGetItem, TestBase):

    def test_getitem_missing_standard_date_fields(self):
        # Eve test uses the Mongo layer directly.
        # TODO: Fix directly in Eve and remove this override
        with self.app.app_context():
            contacts = self.random_contacts(1, False)
            ref = 'test_update_field'
            contacts[0]['ref'] = ref
            self.app.data.insert('contacts', contacts)

        response, status = self.get(self.known_resource, item=ref)
        self.assertItemResponse(response, status)

    def test_getitem_embedded(self):
        # Eve test uses the Mongo layer directly.
        # TODO: Fix directly in Eve and remove this override

        with self.app.app_context():
            fake_contact = self.random_contacts(1)
            fake_contact_id = self.app.data.insert('contacts', fake_contact)[0]
            self.app.data.update('invoices', self.invoice_id,
                                 {'person': fake_contact_id}, None)

        invoices = self.domain['invoices']

        # Test that we get 400 if can't parse dict
        embedded = 'not-a-dict'
        r = self.test_client.get('%s/%s/%s' % (invoices['url'],
                                               self.invoice_id,
                                               '?embedded=%s' % embedded))
        self.assert400(r.status_code)

        # Test that doesn't come embedded if asking for a field that
        # isn't embedded (global setting is True by default)
        embedded = '{"person": 1}'
        r = self.test_client.get('%s/%s/%s' % (invoices['url'],
                                               self.invoice_id,
                                               '?embedded=%s' % embedded))
        self.assert200(r.status_code)
        content = json.loads(r.get_data())
        self.assertTrue(content['person'], self.item_id)

        # Set field to be embedded
        invoices['schema']['person']['data_relation']['embeddable'] = True

        # Test that global setting applies even if field is set to embedded
        invoices['embedding'] = False
        r = self.test_client.get('%s/%s/%s' % (invoices['url'],
                                               self.invoice_id,
                                               '?embedded=%s' % embedded))
        self.assert200(r.status_code)
        content = json.loads(r.get_data())
        self.assertTrue(content['person'], self.item_id)

        # Test that it works
        invoices['embedding'] = True
        r = self.test_client.get('%s/%s/%s' % (invoices['url'],
                                               self.invoice_id,
                                               '?embedded=%s' % embedded))
        self.assert200(r.status_code)
        content = json.loads(r.get_data())
        self.assertTrue('location' in content['person'])

        # Test that it ignores a bogus field
        embedded = '{"person": 1, "not-a-real-field": 1}'
        r = self.test_client.get('%s/%s/%s' % (invoices['url'],
                                               self.invoice_id,
                                               '?embedded=%s' % embedded))
        self.assert200(r.status_code)
        content = json.loads(r.get_data())
        self.assertTrue('location' in content['person'])

        # Test that it ignores a real field with a bogus value
        embedded = '{"person": 1, "inv_number": "not-a-real-value"}'
        r = self.test_client.get('%s/%s/%s' % (invoices['url'],
                                               self.invoice_id,
                                               '?embedded=%s' % embedded))
        self.assert200(r.status_code)
        content = json.loads(r.get_data())
        self.assertTrue('location' in content['person'])

        # Test that it works with item endpoint too
        r = self.test_client.get('%s/%s/%s' % (invoices['url'],
                                               self.invoice_id,
                                               '?embedded=%s' % embedded))
        self.assert200(r.status_code)
        content = json.loads(r.get_data())
        self.assertTrue('location' in content['person'])

        # Test that changes to embedded document invalidate parent cache
        invoice_last_modified = r.headers.get('Last-Modified')
        contact_url = '%s/%s' % (self.domain['contacts']['url'],
                                 fake_contact_id)
        r = self.test_client.get(contact_url)
        contact_etag = r.headers.get('Etag')

        # wait for contact and invoice updated at diff to pass 1s resolution
        time.sleep(2)
        changes = {'location': {'city': 'new city'}}
        response, status = self.patch(contact_url, data=changes,
                                      headers=[('If-Match', contact_etag)])
        self.assert200(status)

        invoice_url = '%s/%s/%s' % (invoices['url'], self.invoice_id,
                                    '?embedded=%s' % embedded)
        r = self.test_client.get(invoice_url,
                                 headers=[('If-Modified-Since',
                                           invoice_last_modified)])
        self.assert200(r.status_code)

    def test_subresource_getitem(self):
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
        response, status = self.get('users/%s/invoices/%s' % (fake_contact_id,
                                                              self.invoice_id))
        self.assert200(status)
        self.assertEqual(response['person'], fake_contact_id)
        self.assertEqual(response['_id'], self.invoice_id)

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_getitem_lookup_field_as_string(self):
        pass

    def test_getitem_with_custom_idfield(self):
        # Eve test uses the Mongo layer directly.
        # TODO: Fix directly in Eve and remove this override
        response, _ = self.get('products')
        sku = response['_items'][0]['sku']
        response, status = self.get('products', item=sku)
        self.assertItemResponse(response, status, 'products')


class TestHead(eve_get_tests.TestHead, TestBase):
    pass


class TestEvents(eve_get_tests.TestEvents, TestBase):

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_on_pre_GET_resource_dynamic_filter_12_chr_nonunicode_string(self):
        pass

    def test_on_fetched_item(self):
        # Eve test casts id_field to string.
        # TODO: Fix directly in Eve and remove this override
        self.app.on_fetched_item += self.devent
        self.get_item()
        self.assertEqual('contacts', self.devent.called[0])
        id_field = self.domain[self.known_resource]['id_field']
        self.assertEqual(self.item_id, self.devent.called[1][id_field])
        self.assertEqual(2, len(self.devent.called))

    def test_on_fetched_item_contacts(self):
        # Eve test casts id_field to string.
        # TODO: Fix directly in Eve and remove this override
        self.app.on_fetched_item_contacts += self.devent
        self.get_item()
        id_field = self.domain[self.known_resource]['id_field']
        self.assertEqual(self.item_id, self.devent.called[0][id_field])
        self.assertEqual(1, len(self.devent.called))
