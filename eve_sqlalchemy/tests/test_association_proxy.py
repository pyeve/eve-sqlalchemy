import simplejson as json
# import pytest
import random
from pprint import pprint

from eve_sqlalchemy.tests import TestBaseSQL

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TestAssociationProxy(TestBaseSQL):

    def test_many_to_many(self):
        """ Simple test case that associates 2 keywords to each product.
        The first keyword is shared by all products and the second is selected
        randomly.
        """
        id_field = self.app.config['ID_FIELD']
        for keyword in ["kw_{:d}".format(i) for i in range(11)]:
            response, status = self.post(
                '/keywords', data={'kw': keyword}
            )
            pprint(response)
        response, status = self.get('keywords')
        pprint(response)
        self.assertTrue('_items' in response)
        self.assertEquals(len(response['_items']), 11)
        keywords = [a[id_field] for a in response['_items']]

        for product in ["product_{:d}".format(i) for i in range(10)]:
            response, status = self.post(
                '/products',
                data={
                    'name': product,
                    'keywords': [
                        keywords[0],
                        keywords[random.choice(range(11))]
                    ]
                }
            )
            pprint(response)

        response, status = self.get('products')
        pprint(response)
        response, status = self.get('products', "?embedded={}".format(json.dumps({'keywords': 1})))
        pprint(response)
        self.assertTrue('_items' in response)
        self.assertEquals(len(response['_items']), 10)
        # products = [a[id_field] for a in response['_items']]
