Installation
============

This part of the documentation covers the installation of Eve-SQLAlchemy. The
first step to using any software package is getting it properly installed.

Installing Eve-SQLAlchemy is simple with `pip
<https://pip.pypa.io/en/stable/>`_:

.. code-block:: console

    $ pip install eve-sqlalchemy


Development Version
-------------------

Eve-SQLAlchemy is actively developed on GitHub, where the code is `always
available <https://github.com/pyeve/eve-sqlalchemy>`_. If you want to work with
the development version of Eve-SQLAlchemy, there are two ways: you can either
let `pip` pull in the development version, or you can tell it to operate on a
git checkout. Either way, virtualenv is recommended.

Get the git checkout in a new virtualenv and run in development mode.

.. code-block:: console

    $ git clone https://github.com/pyeve/eve-sqlalchemy.git
    Cloning into 'eve-sqlalchemy'...
    ...

    $ cd eve-sqlalchemy
    $ virtualenv venv
    ...
    Installing setuptools, pip, wheel...
    done.

    $ . venv/bin/activate
    $ pip install .
    ...
    Successfully installed ...

This will pull in the dependencies and activate the git head as the current
version inside the virtualenv. Then all you have to do is run ``git pull
origin`` to update to the latest version.

To just get the development version without git, do this instead:

.. code-block:: console

    $ mkdir eve-sqlalchemy
    $ cd eve-sqlalchemy
    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install git+https://github.com/pyeve/eve-sqlalchemy.git
    ...
    Successfully installed ...

And you're done!
