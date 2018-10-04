# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from eve import ISSUES, STATUS
from eve.tests.methods import post as eve_post_tests

from eve_sqlalchemy.tests import TestBase, test_sql_tables


class TestPost(eve_post_tests.TestPost, TestBase):

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_post_auto_create_lists(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_post_auto_collapse_multiple_keys(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_post_auto_collapse_media_list(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_dbref_post_referential_integrity(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not implemented yet')
    def test_post_duplicate_key(self):
        """POSTing an already existing key should result in 409, not 422.

        EveMongo does this by not enforcing uniqueness at the validation level,
        but wait until the MongoDB insert fails. They can then easily
        distinguish between a validation error and a duplicate key error.
        """

    def test_post_integer(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.
        test_field = 'prog'
        test_value = 1
        data = {test_field: test_value,
                'ref': 'test_post_integer_1234567'}
        self.assertPostItem(data, test_field, test_value)

    def test_post_list_as_array(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.
        test_field = "role"
        test_value = ["vendor", "client"]
        data = {test_field: test_value,
                'ref': 'test_post_list_as_array_1'}
        self.assertPostItem(data, test_field, test_value)

    def test_post_rows(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.
        test_field = "rows"
        test_value = [
            {'sku': 'AT1234', 'price': 99},
            {'sku': 'XF9876', 'price': 9999}
        ]
        data = {test_field: test_value,
                'ref': 'test_post_rows_1234567890'}
        self.assertPostItem(data, test_field, test_value)

    def test_post_list(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.
        test_field = "alist"
        test_value = ["a_string", 99]
        data = {test_field: test_value,
                'ref': 'test_post_list_1234567890'}
        self.assertPostItem(data, test_field, test_value)

    def test_post_integer_zero(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.
        test_field = "aninteger"
        test_value = 0
        data = {test_field: test_value,
                'ref': 'test_post_integer_zero_12'}
        self.assertPostItem(data, test_field, test_value)

    def test_post_float_zero(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.
        test_field = "afloat"
        test_value = 0.0
        data = {test_field: test_value,
                'ref': 'test_post_float_zero_1234'}
        self.assertPostItem(data, test_field, test_value)

    def test_post_dict(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.
        test_field = "location"
        test_value = {'address': 'an address', 'city': 'a city'}
        data = {test_field: test_value,
                'ref': 'test_post_dict_1234567890'}
        self.assertPostItem(data, test_field, test_value)

    def test_post_datetime(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.
        test_field = "born"
        test_value = "Tue, 06 Nov 2012 10:33:31 GMT"
        data = {test_field: test_value,
                'ref': 'test_post_datetime_123456'}
        self.assertPostItem(data, test_field, test_value)

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_post_objectid(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_post_null_objectid(self):
        pass

    def test_post_default_value_none(self):
        # Eve test manipulates schema and changes type of 'title'. We decided
        # to use different fields for each test.

        # default values that assimilate to None (0, '', False) were ignored
        # prior to 0.1.1
        self.domain['contacts']['schema']['title']['default'] = ''
        self.app.set_defaults()
        data = {"ref": "UUUUUUUUUUUUUUUUUUUUUUUUU"}
        self.assertPostItem(data, 'title', '')

        self.domain['contacts']['schema']['aninteger']['default'] = 0
        self.app.set_defaults()
        data = {"ref": "TTTTTTTTTTTTTTTTTTTTTTTTT"}
        self.assertPostItem(data, 'aninteger', 0)

        self.domain['contacts']['schema']['abool']['default'] = False
        self.app.set_defaults()
        data = {"ref": "QQQQQQQQQQQQQQQQQQQQQQQQQ"}
        self.assertPostItem(data, 'abool', False)

    def test_multi_post_valid(self):
        # Eve test uses mongo layer directly.
        data = [
            {"ref": "9234567890123456789054321"},
            {"ref": "5432112345678901234567890", "role": ["agent"]},
        ]
        r, status = self.post(self.known_resource_url, data=data)
        self.assert201(status)
        results = r['_items']

        self.assertEqual(results[0]['_status'], 'OK')
        self.assertEqual(results[1]['_status'], 'OK')

        r, status = self.get('contacts',
                             '?where={"ref": "9234567890123456789054321"}')
        self.assert200(status)
        self.assertEqual(len(r['_items']), 1)
        r, status = self.get('contacts',
                             '?where={"ref": "5432112345678901234567890"}')
        self.assert200(status)
        self.assertEqual(len(r['_items']), 1)

    def test_multi_post_invalid(self):
        # Eve test uses mongo layer directly and 'tid' is an integer instead of
        # ObjectId for Eve-SQLAlchemy.
        data = [
            {"ref": "9234567890123456789054321"},
            {"prog": 9999},
            {"ref": "5432112345678901234567890", "role": ["agent"]},
            {"ref": self.item_ref},
            {"ref": "9234567890123456789054321", "tid": "foo"},
        ]
        r, status = self.post(self.known_resource_url, data=data)
        self.assertValidationErrorStatus(status)
        results = r['_items']

        self.assertEqual(results[0]['_status'], 'OK')
        self.assertEqual(results[2]['_status'], 'OK')

        self.assertValidationError(results[1], {'ref': 'required'})
        self.assertValidationError(results[3], {'ref': 'unique'})
        self.assertValidationError(results[4], {'tid': 'integer'})

        id_field = self.domain[self.known_resource]['id_field']
        self.assertTrue(id_field not in results[0])
        self.assertTrue(id_field not in results[1])
        self.assertTrue(id_field not in results[2])
        self.assertTrue(id_field not in results[3])

        r, status = self.get('contacts', '?where={"prog": 9999}')
        self.assert200(status)
        self.assertEqual(len(r['_items']), 0)
        r, status = self.get('contacts',
                             '?where={"ref": "9234567890123456789054321"}')
        self.assert200(status)
        self.assertEqual(len(r['_items']), 0)

    def test_post_x_www_form_urlencoded_number_serialization(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.
        test_field = "anumber"
        test_value = 34
        data = {test_field: test_value,
                'ref': 'test_post_x_www_num_ser_1'}
        r, status = self.parse_response(self.test_client.post(
            self.known_resource_url, data=data))
        self.assert201(status)
        self.assertTrue('OK' in r[STATUS])
        self.assertPostResponse(r)

    def test_post_referential_integrity_list(self):
        data = {"invoicing_contacts": [self.item_id, self.unknown_item_id]}
        r, status = self.post('/invoices/', data=data)
        self.assertValidationErrorStatus(status)
        expected = ("value '%s' must exist in resource '%s', field '%s'" %
                    (self.unknown_item_id, 'contacts',
                     self.domain['contacts']['id_field']))
        self.assertValidationError(r, {'invoicing_contacts': expected})

        # Eve test posts a list with self.item_id twice, which can't be handled
        # for our case because we use (invoice_id, contact_id) as primary key
        # in the association table.
        data = {"invoicing_contacts": [self.item_id]}
        r, status = self.post('/invoices/', data=data)
        self.assert201(status)
        self.assertPostResponse(r)

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_post_allow_unknown(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_post_write_concern(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_post_list_of_objectid(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_post_nested_dict_objectid(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_post_valueschema_with_objectid(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_post_list_fixed_len(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_custom_etag_update_date(self):
        pass

    @pytest.mark.xfail(True, run=False, reason='not applicable to SQLAlchemy')
    def test_custom_date_updated(self):
        pass

    def test_post_with_relation_to_custom_idfield(self):
        # Eve test uses mongo layer directly.
        # TODO: Fix directly in Eve and remove this override

        id_field = 'sku'
        r, _ = self.get('products')
        existing_product = r['_items'][0]
        product = {
            id_field: 'BAR',
            'title': 'Foobar',
            'parent_product': existing_product[id_field]
        }
        r, status = self.post('products', data=product)
        self.assert201(status)
        self.assertTrue(id_field in r)
        self.assertItemLink(r['_links'], r[id_field])
        r, status = self.get('products', item='BAR')
        self.assertEqual(r['parent_product'], existing_product[id_field])

    def test_post_dependency_fields_with_default(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.

        # test that default values are resolved before validation. See #353.
        test_field = 'dependency_field2'
        test_value = 'a value'
        data = {test_field: test_value,
                'ref': 'test_post_dep_fields_defa'}
        self.assertPostItem(data, test_field, test_value)

    def test_post_dependency_required_fields(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.

        schema = self.domain['contacts']['schema']
        schema['dependency_field3']['required'] = True
        data = {'ref': 'test_post_dep_req_fields1'}
        r, status = self.post(self.known_resource_url, data=data)
        self.assertValidationErrorStatus(status)
        self.assertValidationError(r, {'dependency_field3': 'required'})

        # required field dependnecy value matches the dependent field's default
        # value. validation still fails since required field is still missing.
        # See #665.
        schema['dependency_field3']['dependencies'] = {'dependency_field1':
                                                       'default'}
        r, status = self.post(self.known_resource_url, data={})
        self.assertValidationErrorStatus(status)
        self.assertValidationError(r, {'dependency_field3': 'required'})

        data = {'dependency_field3': 'hello',
                'ref': 'test_post_dep_req_fields2'}
        r, status = self.post(self.known_resource_url, data=data)
        self.assert201(status)

    def test_post_dependency_fields_with_values(self):
        # Eve test dynamically registers a resource. This is more difficult for
        # SQLAlchemy, so we just use an existing one.

        schema = self.domain['contacts']['schema']
        schema['dependency_field1']['default'] = 'one'
        schema['dependency_field2']['required'] = True
        schema['dependency_field2']['dependencies'] = \
            {'dependency_field1': ['one', 'two']}

        data = {"dependency_field1": "three", "dependency_field2": "seven",
                'ref': 'test_post_dep_fields_val1'}
        r, s = self.post(self.known_resource_url, data=data)
        self.assert422(s)

        data = {"dependency_field2": "seven",
                'ref': 'test_post_dep_fields_val2'}
        r, s = self.post(self.known_resource_url, data=data)
        self.assert201(s)

        data = {"dependency_field1": "one", "dependency_field2": "seven",
                'ref': 'test_post_dep_fields_val3'}
        r, s = self.post(self.known_resource_url, data=data)
        self.assert201(s)

        data = {"dependency_field1": "two", "dependency_field2": "seven",
                'ref': 'test_post_dep_fields_val4'}
        r, s = self.post(self.known_resource_url, data=data)
        self.assert201(s)

    def test_post_dependency_fields_with_subdocuments(self):
        # Eve test dynamically registers a resource. This is more difficult for
        # SQLAlchemy, so we just use an existing one.

        schema = self.domain['contacts']['schema']
        schema['dependency_field2']['dependencies'] = \
            {'location.city': ['Berlin', 'Rome']}

        data = {"location": {"city": "Paris"}, "dependency_field2": "seven",
                'ref': 'test_post_dep_fields_sub1'}
        r, s = self.post(self.known_resource_url, data=data)
        self.assert422(s)

        data = {"location": {"city": "Rome"}, "dependency_field2": "seven",
                'ref': 'test_post_dep_fields_sub2'}
        r, s = self.post(self.known_resource_url, data=data)
        self.assert201(s)

        data = {"location": {"city": "Berlin"}, "dependency_field2": "seven",
                'ref': 'test_post_dep_fields_sub3'}
        r, s = self.post(self.known_resource_url, data=data)
        self.assert201(s)

    def test_post_valueschema_dict(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.

        data = {'valueschema_dict': {'k1': '1'},
                'ref': 'test_post_valueschema_123'}
        r, status = self.post(self.known_resource_url, data=data)
        self.assertValidationErrorStatus(status)
        issues = r[ISSUES]
        self.assertTrue('valueschema_dict' in issues)
        self.assertEqual(issues['valueschema_dict'],
                         {'k1': 'must be of integer type'})

        data['valueschema_dict']['k1'] = 1
        r, status = self.post(self.known_resource_url, data=data)
        self.assert201(status)

    def test_post_propertyschema_dict(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.

        data = {'propertyschema_dict': {'aaa': 1},
                'ref': 'test_post_propertyschema1'}
        r, status = self.post(self.known_resource_url, data=data)
        self.assert201(status)

        data = {'propertyschema_dict': {'AAA': '1'},
                'ref': 'test_post_propertyschema2'}
        r, status = self.post(self.known_resource_url, data=data)
        self.assertValidationErrorStatus(status)

        issues = r[ISSUES]
        self.assertTrue('propertyschema_dict' in issues)
        self.assertEqual(issues['propertyschema_dict'],
                         'propertyschema_dict')

    def test_post_nested(self):
        # Eve test manipulates schema and removes required constraint on 'ref'.
        # We decided to include 'ref' as it is not easy to manipulate
        # nullable-constraints during runtime.

        data = {'location.city': 'a nested city',
                'location.address': 'a nested address',
                'ref': 'test_post_nested_12345678'}
        r, status = self.post(self.known_resource_url, data=data)
        self.assert201(status)
        values = self.compare_post_with_get(
            r[self.domain[self.known_resource]['id_field']],
            ['location']).pop()
        self.assertEqual(values['city'], 'a nested city')
        self.assertEqual(values['address'], 'a nested address')

    def test_id_field_included_with_document(self):
        # Eve test uses ObjectId, we have to use an integer instead.

        # since v0.6 we also allow the id field to be included with the POSTed
        # document
        id_field = self.domain[self.known_resource]['id_field']
        id = 4242
        data = {"ref": "1234567890123456789054321", id_field: id}
        r, status = self.post(self.known_resource_url, data=data)
        self.assert201(status)
        self.assertPostResponse(r)
        self.assertEqual(r['_id'], id)


class TestEvents(eve_post_tests.TestEvents, TestBase):

    def before_insert(self):
        # Eve test code uses mongo layer directy.
        session = self.app.data.driver.session
        model = test_sql_tables.Contacts
        return session.query(model).filter(model.ref == self.new_contact_id) \
                                   .first() is None
