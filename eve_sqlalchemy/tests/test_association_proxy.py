import simplejson as json

from eve_sqlalchemy.tests import TestBaseSQL


class TestAssociationProxy(TestBaseSQL):

    def test_many_to_many(self):
        """ Simple test case that associates 2 keywords to each product.
        The first keyword is shared by all products and the second keyword is
        not shared.
        """
        id_field = self.app.config['ID_FIELD']
        keywords_data = []
        for i in range(11):
            keywords_data.append(
                {'kw': "kw_{0}".format(i)}
            )
        response, status = self.post('/keywords', data=keywords_data)
        self.assertEquals(status, 201)

        response, status = self.get('keywords')
        self.assertTrue('_items' in response)
        self.assertEquals(len(response['_items']), 11)

        keywords = [a[id_field] for a in response['_items']]
        common_keyword = keywords[0]
        products_data = []
        for i in range(10):
            product = "product_{0}".format(i)
            extra_keyword = keywords[i+1]
            products_data.append(
                {
                    'name': product,
                    'keywords': [
                        common_keyword,
                        extra_keyword
                    ]
                }
            )

        response, status = self.post('/products', data=products_data)
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
