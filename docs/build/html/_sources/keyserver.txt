Keyserver
=========

.. py:module:: keyserver.models

The Keyserver is integrated into Pinyto to support webapps. Normally Pinyto uses public-key authentication
which is more secure than username and password. However this method needs clients which create private
and public key pairs and store the private key securely. For webapps this approach is simply not possible.
To solve this the Keyserver stands in between webapps and the cloud and saves one private key for each
username and password. If a webapp wants to authenticate it can send the users credentials to the keyserver
which does the authentication with the stored key if the credentials are correct. The keyserver sends the
decrypted token which is ready to use over an https connection to the webapp. The webapp can use this token
for all requests in this session.

.. autoclass:: Account
   :members:

Administration-API
------------------

.. py:module:: keyserver.views

Similar to the `administration of the cloud <administration.html>`_ does the keyserver provide an API to
administer the Accounts.

.. autofunction:: register

``register`` function expects a "username" and a "password" in the request data.

.. autofunction:: authenticate

``authenticate`` function expects a "username" and a "password" in the request data.

.. autofunction:: change_password

``change_password`` function expects the new password as "password" in the request data.

Urls
++++

.. py:module:: keyserver.urls

.. py:data:: urlpatterns

.. literalinclude:: ../../keyserver/urls.py