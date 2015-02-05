Services
========

Assemblies can only access some services explicitly exposed to them because the sandbox can not allow arbitrary
calls to any library. The services integrated in Pinyto also try to be easy and pleasurable to use.

The database wrapper is already explained in the `Database section <database.html>`_.

Response Helper
---------------

.. py:module:: service.response

Most requests in pinyto expect a response in the form of a HttpResponse object with type "application/json" and
a JSON encoded string as payload. Because this is so common an easy to use helper function is used:

.. autofunction:: json_response

Factory
-------

.. py:module:: service.models

In assemblies it is not allowed to include python modules or classes. Service classes can be instantiated using
the ``Factory`` class which is accessible.

.. autoclass:: Factory
   :members:

The factory can create the following classes:

- Http
- ParseHtml

Http
----

``Http`` uses internally the ``requests`` library from Apache.

.. py:module:: service.http

.. autoclass:: Http
   :members:

ParseHtml
---------

``ParseHtml`` is based on BeautifulSoup version 4. The interface is quite different as the wrapper does not use
a fluid interface.

.. py:module:: service.parsehtml

.. autoclass:: ParseHtml
   :members:

For this class the ``extract_content`` function from ``service.xml`` might become handy.

.. py:module:: service.parsehtml

.. autofunction:: extract_content
