Administration
==============

Pinyto uses two separate databases to store data. The SQL database is used for user accounts,
public-keys, code from assemblies and so on. The real data user store inside of Pinyto is
stored in a document-based database described in `database <database.html>`_. This section is about
the database models and view functions used for registration, authentication and
administration.

In Pinyto all api calls accept only json data for parameters and payload data. Every request except
registration and authentication must contain a "token" which identifies the current user and her
permissions. An example would be ``{"token": "12323A38B3", "name": "test", "author": "mustermann"}``.

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

Registering new accounts is done in the register function in views.py.

.. autofunction:: register

Although the register function does the real work it does not accept a Django request object as parameter
and is therefore not fit to be called by the url dispatcher. For this task the register_request function
exists which accepts a request object and can easily be referenced in the url configuration. It internally
calls register after extracting relevant the request data.

.. autofunction:: register_request

Registration requests must supply json-encoded data with a "username" and "key_data" while the key_data
itself consists of a "N" and "e" value. Supply the numbers as strings.

Example: ``{"username": "MaxMustermann", "key_data": {"N": "123456789123456789213456", "e": "54263"}}``
For a real key N must be a much bigger number.

Authentication
--------------

Similar to the registration the authentication also consists of two functions. The real work is done in
``authenticate``:

.. autofunction:: authenticate

The matching function which accepts requests and which is wired into the url config is:

.. autofunction:: authenticate_request

The authentication request needs a "username" and a "key_hash" which identifies the public key used for
authentication. The key_hash consists of the first 10 bytes of a sha256 hash of (N+e).

Authenticate returns a challenge for this request containing an encrypted token and a signature of this
token signed with the key of the server. The client can check the signature to verify the identity of
the server. The client also decrypts the token with the private key matching the public key which was used
for the hash in the request. By encrypting the token the server makes sure that only the client which
possesses the private key can decrypt the token and use it for authentication.

Authenticate starts a session with a token which is transmitted with every request and which is used to
identify the client and ensure that no attacker can access api functions without a correct token. If an
attacker reads the token he can make requests as he likes as long as the session is active. Because of
that the whole connection must be secured with https and the client must make sure the token is not
accessed by malware.

Logout
------

``logout`` only needs a "token".

.. autofunction:: logout

Key Management
--------------
There are four functions for the key management. ``list_keys`` lists all public keys of the user:

.. autofunction:: list_keys

Each key listed by this function should match a device used for Pinyto. The first key is usually the one
used by webapps like the backoffice.

If a key is to be added ``register_new_key`` is called:

.. autofunction:: register_new_key

The function accepts "key_data" with a "N" and "e" encoded as strings.

Keys can also be deleted:

.. autofunction:: delete_key

``delete_key`` expects a "key_hash" with the first 10 bytes of a sha256 hash of (str(N)+str(e)).

Keys can be deactivated and deactivated again. For this functionality there is only one function which
accepts the state:

.. autofunction:: set_key_active

The function needs a "key_hash" which identifies the key and an "active_state" as a boolean.

Assembly Management
-------------------

Assemblies in Pinyto belong to a user but any user can install them. So it is important to distinguish
between the assemblies owned by the user which she can edit and the ones owned by other users which can
only be installed and deinstalled.

save_assembly
+++++++++++++

If a user wants to save a new assembly she can use this function:

.. autofunction:: save_assembly

``save_assembly`` accepts all the data defining an assembly in one big json datastructure:

- "original_name" is the name the assembly had. If the original_name does not specify an assembly of
  the user a new assembly is created using the data from "data".
- "data" contains the data of the assembly as it should be after it is saved to the database.
    - "name" is the new name of the assembly.
    - "description" is the new description.
    - "api_functions" is a list of dictionaries containing:
        - "name" - the name of the function
        - "code" - the code of the function
    - "jobs" is a list of dictionaries containing:
        - "name" - the name of the job
        - "code" - the code of the job
        - "schedule" - an integer defining how many minutes the cloud should wait until running the job
          again. 0 means the job is run only once.

``save_assembly`` returns ``{"success": true}`` if the assembly is saved.

delete_assembly
+++++++++++++++

.. autofunction:: delete_assembly

Call ``delete_assembly`` with a "name" defining an existing assembly of this user.

``delete_assembly`` returns ``{"success": true}`` if the assembly is deleted.

list_own_assemblies
+++++++++++++++++++

.. autofunction:: list_own_assemblies

list_all_assemblies
+++++++++++++++++++

This function lists all assemblies, the ones of the user and all assemblies which could be installed by the user,

.. autofunction:: list_all_assemblies

get_assembly_source
+++++++++++++++++++

In many cases the description of an assembly is not sufficient for the user to decide if she can safely install
the assembly. With the following function the complete sourcecode of the assembly can be loaded:

.. autofunction:: get_assembly_source

The assembly is specified with an "author" and a "name". If written as a combination it is ``author/name``.

install_assembly
++++++++++++++++

If the user decides that an assembly is useful and not harmful she can install the assembly with
``install_assembly``.

.. autofunction:: install_assembly

The assembly is specified with an "author" and a "name". If written as a combination it is ``author/name``.

uninstall_assembly
++++++++++++++++++

.. autofunction:: uninstall_assembly

The assembly is specified with an "author" and a "name". If written as a combination it is ``author/name``.

list_installed_assemblies
+++++++++++++++++++++++++

This function lists only the installed assemblies of the user.

.. autofunction:: list_installed_assemblies

Urls
----

.. py:module:: pinytoCloud.urls

Below is the main URL configuration in ``pinytoCloud/urls.py`` which also includes the urls from keyserver and
the api calls handeled in api_prototype.

.. py:data:: urlpatterns

.. literalinclude:: ../../pinytoCloud/urls.py