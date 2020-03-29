Eve-SQLAlchemy extension
========================

.. image:: https://travis-ci.org/pyeve/eve-sqlalchemy.svg?branch=master
   :target: https://travis-ci.org/pyeve/eve-sqlalchemy

Powered by Eve, SQLAlchemy and good intentions this extension allows
to effortlessly build and deploy highly customizable, fully featured
RESTful Web Services with SQL-based backends.

Eve-SQLAlchemy is simple
------------------------

The following code blocks are excerpts of ``examples/one_to_many`` and should
give you an idea of how Eve-SQLAlchemy is used. A complete working example can
be found there. If you are not familiar with `Eve <https://python-eve.org/>`_
and `SQLAlchemy <https://www.sqlalchemy.org/>`_, it is recommended to read up
on them first.

For this example, we declare two SQLAlchemy mappings (from ``domain.py``):

.. code-block:: python

    class Parent(BaseModel):
        __tablename__ = 'parent'
        id = Column(Integer, primary_key=True)
        children = relationship("Child")

    class Child(BaseModel):
        __tablename__ = 'child'
        id = Column(Integer, primary_key=True)
        parent_id = Column(Integer, ForeignKey('parent.id'))

As for Eve, a ``settings.py`` is used to configure our API. Eve-SQLAlchemy,
having access to a lot of metadata from your models, can automatically generate
a great deal of the `DOMAIN` dictionary for you:

.. code-block:: python

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESOURCE_METHODS = ['GET', 'POST']

    DOMAIN = DomainConfig({
        'parents': ResourceConfig(Parent),
        'children': ResourceConfig(Child)
    }).render()

Finally, running our application server is easy (from ``app.py``):

.. code-block:: python

    app = Eve(validator=ValidatorSQL, data=SQL)

    db = app.data.driver
    Base.metadata.bind = db.engine
    db.Model = Base

    # create database schema on startup and populate some example data
    db.create_all()
    db.session.add_all([Parent(children=[Child() for k in range(n)])
                        for n in range(10)])
    db.session.commit()

    # using reloader will destroy the in-memory sqlite db
    app.run(debug=True, use_reloader=False)

The API is now live, ready to be consumed:

.. code-block:: console

    $ curl -s http://localhost:5000/parents | python -m json.tool

.. code-block:: json

    {
        "_items": [
            {
                "_created": "Sun, 22 Oct 2017 07:58:28 GMT",
                "_etag": "f56d7cb013bf3d8449e11e8e1f0213f5efd0f07d",
                "_links": {
                    "self": {
                        "href": "parents/1",
                        "title": "Parent"
                    }
                },
                "_updated": "Sun, 22 Oct 2017 07:58:28 GMT",
                "children": [],
                "id": 1
            },
            {
                "_created": "Sun, 22 Oct 2017 07:58:28 GMT",
                "_etag": "dd1698161cb6beef04f564b2e18804d4a7c4330d",
                "_links": {
                    "self": {
                        "href": "parents/2",
                        "title": "Parent"
                    }
                },
                "_updated": "Sun, 22 Oct 2017 07:58:28 GMT",
                "children": [
                    1
                ],
                "id": 2
            },
            "..."
        ],
        "_links": {
            "parent": {
                "href": "/",
                "title": "home"
            },
            "self": {
                "href": "parents",
                "title": "parents"
            }
        },
        "_meta": {
            "max_results": 25,
            "page": 1,
            "total": 10
        }
    }

All you need to bring your API online is a database, a configuration
file (defaults to ``settings.py``) and a launch script.  Overall, you
will find that configuring and fine-tuning your API is a very simple
process.

Eve-SQLAlchemy is thoroughly tested under Python 2.7-3.7 and PyPy.

Documentation
-------------

The offical project documentation can be accessed at
`eve-sqlalchemy.readthedocs.org
<https://eve-sqlalchemy.readthedocs.org/>`_. For full working examples,
especially regarding different relationship types, see the ``examples``
directory in this repository.
