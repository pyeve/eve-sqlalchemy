Create a file, called trivial.py, and inclue the following:

.. literalinclude:: ../examples/trivial.py

Run this command to start the server:

    python trivial.py

Open the following in your browser to confirm that the server is serving: 

    http://127.0.0.1:5000/

You will see something like this:

    <resource>
    <link rel="child" href="invoices" title="invoices"/>
    <link rel="child" href="people" title="people"/>
    </resource>

Now try the people URL:

    http://127.0.0.1:5000/people

You will see the three records we preloaded.

    <resource href="people" title="people">
    <link rel="parent" href="/" title="home"/><_meta><max_results>25</max_results><page>1</page><total>3</total></_meta><resource><_created/><_etag/><_updated>Sun, 22 Feb 2015 16:28:00 GMT</_updated><firstname>George</firstname><fullname>George Washington</fullname><id>1</id><lastname>Washington</lastname></resource>
    ... etc ...

