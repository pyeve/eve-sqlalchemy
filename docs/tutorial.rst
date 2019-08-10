Tutorial
========

The example app used by this tutorial is available at ``examples/simple`` inside
the Eve-SQLAlchemy repository.

Schema registration
-------------------
The main goal of the `SQLAlchemy`_ integration in Eve is to separate
dependencies and keep model registration depend only on sqlalchemy
library. This means that you can simply use something like that:

.. literalinclude:: ../eve_sqlalchemy/examples/simple/tables.py

We have used ``CommonColumns`` abstract class to provide attributes used by
Eve, such as ``_created`` and ``_updated``. These are not needed if you are only
reading from the database. However, if your API is also writing to the database,
then you need to include them.


Eve settings
------------
All standard Eve settings will work with `SQLAlchemy`_ support. However, you
need to manually decide which `SQLAlchemy`_ declarative classes you wish to
register. You can do so using ``DomainConfig`` and ``ResourceConfig``, which
will give you a default schema (``DOMAIN`` dictionary) derived from your
`SQLAlchemy`_ models. This is intended as a starting point and to save you
from redundant configuration, but there's nothing wrong with customizing this
dictionary if you need to!

.. literalinclude:: ../eve_sqlalchemy/examples/simple/settings.py

A note about using ``update``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A common mistake is to use ``update`` to try to update values in a nested
dictionary. This will overwrite the entire dictionary and probably cause
``KeyError``\s.

.. code-block:: python

    # Instead of this...
    DOMAIN['foo'].update({
      'datasource': {  # 'datasource' will only contain 'default_sort'!
        'default_sort': [('id', -1)]
      }
    })
    # ... do this:
    DOMAIN['foo']['datasource']['default_sort'] = [('id', -1)]


Authentication example
----------------------
This example is based on the Token-Based tutorial from `Eve Authentication`_.
First we need to create eve-side authentication:

.. code-block:: python

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

    from werkzeug.security import generate_password_hash, \
        check_password_hash

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

        def encrypt(self, password):
            """Encrypt password using werkzeug security module.
            """
            return generate_password_hash(password)

        @validates('password')
        def _set_password(self, key, value):
            """Using SQLAlchemy validation makes sure each
            time password is changed it will get encrypted
            before flushing to db.
            """
            return self.encrypt(value)

        def check_password(self, password):
            if not self.password:
                return False
            return check_password_hash(self.password, password)


And finally a flask login view:

.. code-block:: python

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
            data = request.get_json()
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

.. code-block:: python

    app = Eve(validator=ValidatorSQL, data=SQL)
    db = app.data.driver
    Base.metadata.bind = db.engine
    db.Model = Base

Now you can run Eve:

.. code-block:: python

   app.run(debug=True)

and start it:

.. code-block:: console

    $ python app.py
     * Running on http://127.0.0.1:5000/

and check that everything is working like expected, by trying requesting
`people`:

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

Query strings are supported, allowing for filtering and sorting. Both native
Mongo queries and Python conditional expressions are supported. For more
examples please check `SQLAlchemy filtering`_.

Filtering
~~~~~~~~~
**Generating 'exact' matches**

Here we are asking for all `people` where `lastname` value is `Smith`:

.. code-block:: console

    /people?where={"lastname":"Smith"}

which produces where closure:

.. code-block:: sql

   people.lastname = "Smith"

**Generating multiple 'exact' matches**

Here we are asking for all `people` where `age` value is between `50` and `60`:

.. code-block:: console

    /people?where=age>50 and age<60

which produces where closure:

.. code-block:: sql

   people.age > 50 AND people.age < 60

**Generating 'like' matches**

Here we are asking for all `people` where `lastname` value contains `Smi`:

.. code-block:: console

    /people?where={"lastname":"like(\"Smi%\")"}

which produces where closure:

.. code-block:: sql

   people.lastname LIKE "Smi%"

**Generating 'in' matches**

Here we are asking for all `people` where `firstname` value is `John` or `Fred`:

.. code-block:: console

    /people?where={"firstname":"in(\"(\'John\',\'Fred\')\")"}

or you can also use the other syntax query

.. code-block:: console

    /people?where={"firstname":['John','Fred']}

which produces where closure:

.. code-block:: sql

   people.firstname IN ("John", "Fred")

**Generating 'similar to' matches**

.. code-block:: console

    /people?where={"firstname":"similar to(\"(\'%ohn\'|\'%acob\')\")"}

which produces where closure:

.. code-block:: sql

   people.firstname SIMILAR TO '("%ohn"|"%acob")'

**Generating 'any' matches**

If you have postgresql ARRAY column you can use `any`:

.. code-block:: console

    /documents?where={"keywords":"any(\"critical\")"}

which produces where closure:

.. code-block:: sql

   "critical" = ANY(documents.keywords)

**Generating 'not null' matches**

.. code-block:: console

    /documents?where={"keywords":"!=null"}

which produces where closure:

.. code-block:: sql

   documents.keywords IS NOT NULL

**Generating 'datetime' matches**

Here we are asking for all `documents` that where `_created` after
`Mon, 17 Oct 2019 03:00:00 GMT`:

.. code-block:: console

    /documents?where=_created> \"Mon, 17 Oct 2019 03:00:00 GMT\"

which produces where closure:

.. code-block:: sql

   documents._created > 2019-10-17 03:00:00

Sorting
~~~~~~~
Starting from version 0.2 you can use `SQLAlchemy ORDER BY`_ expressions such
as: `nullsfirst`, `nullslast`, etc.

Using those expresssion is straightforward, just pass it as 3 argument to
sorting:

.. code-block:: console

    /people?sort=[("lastname", -1, "nullslast")]

which produces order by expression:

.. code-block:: sql

   people.lastname DESC NULLS LAST

You can also use the following python-Eve syntax:

.. code-block:: console

    /people?sort=lastname,-created_at

FAQ
~~~
**cURL**

Keep in mind that every browser or cURL generator can implement its own encoder,
and not all produce the same result. So, adding `--data-urlencode` to the curl
query should work.

.. code-block:: console

    curl -iG --data-urlencode where='_created> "Thu, 22 Nov 2018 09:00:00 GMT"' localhost:5000/people

Embedded resources
------------------

Eve-SQLAlchemy support the embedded keyword of python-eve (`Eve Embedded
Resource Serialization`_).

.. code-block:: console

    /people?embedded={"address":1}

For example, the following request will list the people and embedded their
addresses.

Starting from version 0.4.0a, only the fields that have the projection (`Eve
Projections`_) enabled are included in the associated resource. This was
necessary to avoid endless loops when relationship between resources were
referring each other.


.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _Flask-SQLAlchemy: http://flask-sqlalchemy.pocoo.org/
.. _SQLAlchemy internals: http://docs.sqlalchemy.org/en/latest/orm/internals.html
.. _SQLAlchemy filtering: http://docs.python-eve.org/en/latest/features.html#filtering
.. _SQLAlchemy ORDER BY: http://docs.sqlalchemy.org/en/latest/core/sqlelement.html#sqlalchemy.sql.expression.nullsfirst
.. _`Eve Authentication`: http://python-eve.org/authentication.html#token-based-authentication
.. _`Eve Embedded Resource Serialization`: http://python-eve.org/features.html#embedded-resource-serialization
.. _`Eve Projections`: http://python-eve.org/features.html#projections
