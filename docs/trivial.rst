Simple example
==============

Create a file, called trivial.py, and include the following:

.. literalinclude:: ../eve_sqlalchemy/examples/trivial/trivial.py

Run this command to start the server:

.. code-block:: console

    python trivial.py

Open the following in your browser to confirm that the server is serving:

.. code-block:: console

    http://127.0.0.1:5000/

You will see something like this:

.. code-block:: xml

    <resource>
        <link rel="child" href="people" title="people"/>
    </resource>

Now try the people URL:

.. code-block:: console

    http://127.0.0.1:5000/people

You will see the three records we preloaded.

.. code-block:: xml

    <resource href="people" title="people">
        <link rel="parent" href="/" title="home"/>
        <_meta>
            <max_results>25</max_results>
            <page>1</page>
            <total>3</total>
        </_meta>
        <_updated>Sun, 22 Feb 2015 16:28:00 GMT</_updated>
        <firstname>George</firstname>
        <fullname>George Washington</fullname>
        <id>1</id>
        <lastname>Washington</lastname>
    </resource>
