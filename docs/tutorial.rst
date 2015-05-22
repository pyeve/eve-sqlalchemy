.. _tutorial:

Tutorial
========
The example app used by this tutorial is available at ``examples`` inside
Eve repository.

Schema registration
-------------------
The main goal of the `SQLAlchemy`_ integration in Eve is to separate dependencies
and keep model registration depend only on sqlalchemy library. This means that
you can simply use something like that:

.. literalinclude:: ../examples/tables.py
   :lines: 6-19,34-40,46-

We have used ``CommonColumns`` abstract class to provide attributes used by Eve,
such us ``_created`` and ``_updated``, but you are not forced to used them:

.. literalinclude:: ../examples/tables.py
   :lines: 20-24


Eve settings
------------
All standard Eve settings will work with `SQLAlchemy`_ support. However, you need
manually decide which `SQLAlchemy`_ declarative classes you wish to register.
You can do it using ``registerSchema``:

.. literalinclude:: ../examples/settings.py
   :lines: 9-13, 25-29

As you noticed the schema will be stored inside `_eve_schema` class attribute
so it can be easily used. You can of course extend the autogenerate schema
with your custom options:

.. literalinclude:: ../examples/settings.py
   :lines: 31-


Authentication example
----------------------
This example is based on the Token-Based tutorial from `Eve Authentication`_. 
First we need to create eve-side authentication:

.. code-block:: python

    # -*- coding: utf-8 -*-

    """
    Auth-Token
    ~~~~~~~~~~

    Securing an Eve-powered API with Token based Authentication and
    SQLAlchemy.

    This snippet by Andrew Mleczko can be used freely for anything
    you like. Consider it public domain.
    """


    from eve import Eve
    from eve.auth import TokenAuth
    from .models import User
    from .views import register_views


    class TokenAuth(TokenAuth):
        def check_auth(self, token, allowed_roles, resource, method):
            """First we are verifying if the token is valid. Next
            we are checking if user is authorized for given roles.
            """
            login = User.verify_auth_token(token)
            if login and allowed_roles:
                user = app.data.driver.session.query(User).get(login)
                return user.isAuthorized(allowed_roles)
            else:
                return False


    if __name__ == '__main__':
        app = Eve(auth=TokenAuth)
        register_views(app)
        app.run()

Next step is the `User` SQLAlchemy model:

.. code-block:: python

    # -*- coding: utf-8 -*-

    """
    Auth-Token
    ~~~~~~~~~~

    Securing an Eve-powered API with Token based Authentication and
    SQLAlchemy.

    This snippet by Andrew Mleczko can be used freely for anything
    you like. Consider it public domain.
    """

    import hashlib
    import string
    import random

    from itsdangerous import TimedJSONWebSignatureSerializer \
        as Serializer
    from itsdangerous import SignatureExpired, BadSignature

    from sqlalchemy.orm import validates
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()
    SECRET_KEY = 'this-is-my-super-secret-key'


    class User(Base):
        __tablename__ = 'users'

        login = Column(String, primary_key=True)
        password = Column(String)
        roles = relationship("Role", backref="users")

        def generate_auth_token(self, expiration=24*60*60):
            """Generates token for given expiration
            and user login."""
            s = Serializer(SECRET_KEY, expires_in=expiration)
            return s.dumps({'login': self.login })

        @staticmethod
        def verify_auth_token(token):
            """Verifies token and eventually returns
            user login.
            """
            s = Serializer(SECRET_KEY)
            try:
                data = s.loads(token)
            except SignatureExpired:
                return None # valid token, but expired
            except BadSignature:
                return None # invalid token
            return data['login']

        def isAuthorized(self, role_names):
            """Checks if user is related to given role_names.
            """
            allowed_roles = set([r.id for r in self.roles])\
                .intersection(set(role_names))
            return len(allowed_roles) > 0

        def generate_salt(self):
            return ''.join(random.sample(string.letters, 12))

        def encrypt(self, password):
            """Encrypt password using hashlib and current salt.
            """
            return str(hashlib.sha1(password + str(self.salt))\
                .hexdigest())

        @validates('password')
        def _set_password(self, key, value):
            """Using SQLAlchemy validation makes sure each
            time password is changed it will get encrypted
            before flushing to db.
            """
            self.salt = self.generate_salt()
            return self.encrypt(value)

        def check_password(self, password):
            if not self.password:
                return False
            return self.encrypt(password) == self.password


And finally a flask login view:

.. code-block:: python

    # -*- coding: utf-8 -*-

    """
    Auth-Token
    ~~~~~~~~~~

    Securing an Eve-powered API with Token based Authentication and
    SQLAlchemy.

    This snippet by Andrew Mleczko can be used freely for anything
    you like. Consider it public domain.
    """

    import json
    import base64

    from flask import request, jsonify
    from werkzeug.exceptions import Unauthorized
    from .models import User


    def register_views(app):

        @app.route('/login', methods=['POST'])
        def login(**kwargs):
            """Simple login view that expect to have username
            and password in the request POST. If the username and
            password matches - token is being generated and return.
            """
            data = json.loads(request.data)
            login = data.get('username')
            password = data.get('password')

            if not login or not password:
                raise Unauthorized('Wrong username and/or password.')
            else:
                user = app.data.driver.session.query(User).get(login)
                if user and user.check_password(password):
                    token = user.generate_auth_token()
                    return jsonify({'token': token.decode('ascii')})
            raise Unauthorized('Wrong username and/or password.')


Start Eve
---------
That's almost everything. Before you can start Eve you need to bind SQLAlchemy
from the Eve data driver:

.. literalinclude:: ../examples/sqla_example.py
   :lines: 1-11

Now you can run Eve:

.. code-block:: python

   app.run(debug=True)

and start it:

.. code-block:: console

    $ python sqla_example.py
     * Running on http://127.0.0.1:5000/

and check that everything is working like expected, by trying requesting `people`:

.. code-block:: console

    $ curl http://127.0.0.1:5000/people/1

::

    {
        "id": 1,
        "fullname": "George Washington",
        "firstname": "George",
        "lastname": "Washington",
        "_etag": "31a6c47afe9feb118b80a5f0004dd04ee2ae7442",
        "_created": "Thu, 21 Aug 2014 11:18:24 GMT",
        "_updated": "Thu, 21 Aug 2014 11:18:24 GMT",
        "_links": {
            "self": {
                "href":"/people/1",
                "title":"person"
            },
            "parent": {
                "href": "",
                "title": "home"
            },
            "collection": {
                "href": "/people",
                "title": "people"
            }
        },
    }

Using Flask-SQLAlchemy
----------------------
If you are using `Flask-SQLAlchemy`_, you can use your existing ``db``
object in the ``SQL`` class driver, rather than the empty one it creates.

You can do this by subclassing ``SQL`` and overriding the driver.

.. code-block:: python

   from eve_sqlalchemy import SQL as _SQL
   from flask_sqlalchemy import SQLAlchemy
   
   db = SQLAlchemy(app)
   
   class SQL(_SQL):
      driver = db
   
   app = Eve(validator=ValidatorSQL, data=SQL)

SQLAlchemy expressions
----------------------
With this version of Eve you can use `SQLAlchemy`_ expressions such as: `like`,
`in`, `any`, etc. For more examples please check `SQLAlchemy internals`_.

Using those expresssion is straightforward (you can use them only with dictionary
where filter):

.. code-block:: console

    http://127.0.0.1:5000/people?where={"lastname":"like(\"Smi%\")"}

which produces where closure:

.. code-block:: sql

   people.lastname LIKE "Smi%"

Another examples using `in`:

.. code-block:: console

    http://127.0.0.1:5000/people?where={"firstname":"in(\"(\'John\',\'Fred\'\"))"}

which produces where closure:

.. code-block:: sql

   people.firstname IN ("John", "Fred")

Another examples using `similar to`:

.. code-block:: console

    http://127.0.0.1:5000/people?where={"firstname":"similar to(\"(\'%ohn\'|\'%acob\'\"))"}

which produces where closure:

.. code-block:: sql

   people.firstname SIMILAR TO '("%ohn"|"%acob")'

and if you have postgresql ARRAY column you can use `any`:

.. code-block:: console

    http://127.0.0.1:5000/documents?where={"keywords":"any(\"critical\")"}

which produces where closure:

.. code-block:: sql

   "critical" = ANY(documents.keywords)

SQLAlchemy sorting
------------------
Starting from version 0.2 you can use `SQLAlchemy ORDER BY`_ expressions such as: `nullsfirst`,
`nullslast`, etc.

Using those expresssion is straightforward, just pass it as 3 argument to sorting:

.. code-block:: console

    http://127.0.0.1:5000/people?sort=[("lastname", -1, "nullslast")]

which produces order by expression:

.. code-block:: sql

   people.lastname DESC NULLS LAST

You can also support the following python-Eve syntax:

.. code-block:: console

    http://127.0.0.1:5000/people?sort=lastname,-created_at

How to adjust the primary column name
-------------------------------------

Eve use the `_id` column as primary id field. This is the default value of the MongoDB database.
In SQL, it much more common to call this column just `id`. You can do that with the following
change in your `settings.py`:

.. code-block:: python

    from eve.utils import config

    ID_FIELD = 'id'
    ITEM_LOOKUP_FIELD = ID_FIELD
    config.ID_FIELD = ID_FIELD
    config.ITEM_LOOKUP_FIELD = ID_FIELD

    registerSchema('people')(People)

    DOMAIN = {
        'people': People._eve_schema['people'],
    }

Embedded resources
------------------

Eve-SQLAlchemy support the embedded keyword of python-eve ( `Eve Embedded Resource Serialization`_ ).

.. code-block:: console

    http://127.0.0.1:5000/people?embedded={"address":1}

For example, the following request will list the people and embedded their addresses.

Starting from version 0.3.5, only the fields that have the projection (`Eve Projections`) enabled are included
in the associated resource. This was necessary to avoid endless loop when relationship between resources were
refeering each others.


.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _Flask-SQLAlchemy: http://flask-sqlalchemy.pocoo.org/
.. _SQLAlchemy internals: http://docs.sqlalchemy.org/en/latest/orm/internals.html
.. _SQLAlchemy ORDER BY: http://docs.sqlalchemy.org/en/latest/core/sqlelement.html#sqlalchemy.sql.expression.nullsfirst
.. _`Eve Authentication`: http://python-eve.org/authentication.html#token-based-authentication
.. _`Eve Embedded Resource Serialization`: http://python-eve.org/features.html#embedded-resource-serialization
.. _`Eve Projections`: http://python-eve.org/features.html#projections
