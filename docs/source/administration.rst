Administration
==============

Pinyto uses two separate databases to store data. The SQL database is used for user accounts,
public-keys, code from assemblies and so on. The real data user store inside of Pinyto is
stored in a document-based database described in `database <database.html>`_. This section is about
the database models and view functions used for registration, authentication and
administration.

.. py:module:: pinytoCloud.models

Users
-----

Users are saved in this class:

.. autoclass:: User
   :members:

As users need to get initialized with empty budgets a function is needed which is hooked into the
``post_init`` signal from Django:

.. autofunction:: initialize_budgets

Public Keys
-----------

Users have one public key for each device they use to connect to the cloud. This class saves the
key:

.. autoclass:: StoredPublicKey
   :members:

Sessions
--------

If a user authenticates at the cloud a session is created. Each session has a random token which has
to be present at all requests a user makes.

.. autoclass:: Session
   :members:

The user's code
---------------

Users can write their own assemblies and they are stored in the following objects. The Assembly class
stores the basic information about the assembly while ApiFunction an Job store the code.

Assembly
++++++++

.. autoclass:: Assembly
   :members:

ApiFunction
+++++++++++

.. autoclass:: ApiFunction
   :members:

Job
+++

.. autoclass:: Job
   :members:

Registration
------------

.. py:module:: pinytoCloud.views

.. autofunction:: register

