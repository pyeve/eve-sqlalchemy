import simplejson as json

from eve_sqlalchemy.tests import TestBaseSQL


class TestAssociationProxy(TestBaseSQL):
    """ Simple test case that associates 2 keywords to each product.
    The first keyword is shared by all products and the second keyword is
    not shared.
    """

    def setUp(self, *args, **kwargs):
        """ Create 11 keywords.
        """
        TestBaseSQL.setUp(self, *args, **kwargs)

        self.id_field = self.app.config['ID_FIELD']

        self.keywords_data = []
        for i in range(11):
            self.keywords_data.append(
                {'kw': "kw_{0}".format(i)}
            )
        response, status = self.post('/keywords', data=self.keywords_data)
        self.assertEquals(status, 201)

        response, status = self.get('keywords')
        self.assertTrue('_items' in response)
        self.assertEquals(len(response['_items']), 11)

        self.keywords = response['_items']
        self.shared_keyword = self.keywords[0][self.id_field]

        self.products_data = []

    def test_post_products(self):
        """ Create 10 products with 2 keywords as previously described.
        """
        for i in range(10):
            product = "product_{0}".format(i)
            extra_keyword = self.keywords[i+1][self.id_field]
            self.products_data.append(
                {
                    'name': product,
                    'keywords': [
                        self.shared_keyword,
                        extra_keyword
                    ]
                }
            )

        response, status = self.post('/products', data=self.products_data)
        self.assertEquals(status, 201)

        response, status = self.get(
            'products',
            "?embedded={0}".format(json.dumps({'keywords': 1}))
        )
        self.assertEquals(status, 200)
        self.assertTrue('_items' in response)
        _items = response['_items']
        self.assertEquals(len(_items), 10)
        for item in _items:
            self.assertTrue('keywords' in item)
            self.assertEquals(len(item['keywords']), 2)
        return True

    def test_get_dict_query(self):
        """ Retrieve products by some of their keywords attributes.
        """
        self.test_post_products()

        # Get any products with keywords(_id=2)
        query_by_id = "?embedded={0}&where={1}".format(
            json.dumps({'keywords': 1}),
            json.dumps({'keywords': {'_id': 2}})
        )
        response, status = self.get('products', query_by_id)
        self.assertEquals(status, 200)
        self.assertTrue('_items' in response)
        _items = response['_items']
        self.assertEquals(len(_items), 1)
        self.assertEquals(_items[0]['name'], 'product_0')

        # Get any products with keywords(kw='kw_3')
        query_by_kw = "?embedded={0}&where={1}".format(
            json.dumps({'keywords': 1}),
            json.dumps({'keywords': {'kw': 'kw_3'}})
        )
        response, status = self.get('products', query_by_kw)
        self.assertEquals(status, 200)
        self.assertTrue('_items' in response)
        _items = response['_items']
        self.assertEquals(len(_items), 1)
        self.assertEquals(_items[0]['name'], 'product_2')
