Eve SQLAlchemy extension
========================

.. image:: https://travis-ci.org/RedTurtle/eve-sqlalchemy.svg?branch=master
   :target: https://travis-ci.org/RedTurtle/eve-sqlalchemy


.. image:: https://coveralls.io/repos/RedTurtle/eve-sqlalchemy/badge.svg?branch=master
   :target: https://coveralls.io/r/RedTurtle/eve-sqlalchemy?branch=master


.. image:: https://landscape.io/github/RedTurtle/eve-sqlalchemy/master/landscape.svg?style=flat
   :target: https://landscape.io/github/RedTurtle/eve-sqlalchemy/master



Powered by Eve, SQLAlchemy and good intentions this extenstion allows to 
effortlessly build and deploy highly customizable, fully featured RESTful Web 
Services with SQL-based backends.

Eve SQLAlchemy is Simple
------------------------
.. code-block:: python

    from eve import Eve
    from eve_sqlalchemy import SQL

    app = Eve(data=SQL)
    app.run()

The API is now live, ready to be consumed:

.. code-block:: console

    $ curl -i http://example.com/people
    HTTP/1.1 200 OK

All you need to bring your API online is a database, a configuration file
(defaults to ``settings.py``) and a launch script.  Overall, you will find that
configuring and fine-tuning your API is a very simple process.

Eve is thoroughly tested under Python 2.6, 2.7, 3.3, 3.4 and PyPy.

Make sure you check both these websites:

- `Official Eve Website <http://python-eve.org/>`_
- `Eve-SQLAlchemy Tutorials and Howtos <http://eve-sqlalchemy.readthedocs.org/>`_

