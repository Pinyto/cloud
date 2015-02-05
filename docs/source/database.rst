Database
========

Wrapper-Service
---------------

.. py:module:: service.database

Pinyto internally uses pymongo to access the `MongoDB <http://www.mongodb.org/>`_ database on the server.
Because of the restrictive sandbox architecture a wrapper service for the database interface is used which
basically exposes the most used functionality of pymongo to the assemblies. For security reasons no direct
access to pymongo could be allowed because Pinyto must make sure the data of other users stays untouched.

.. autoclass:: CollectionWrapper
   :members:

For coders the helpers used in this service may be of interest:

.. autofunction:: encode_underscore_fields

.. autofunction:: encode_underscore_fields_list

.. autofunction:: inject_object_id

Default-API
-----------

Some API functions are used in nearly every assembly. To prevent users from writing the same code over and over
some default functions for assemblies are implemented and can be called by every assembly.

.. warning::
    Default API-functions hide explicitly defined functions in the assembly with the same name at the moment. This
    may change in future versions where assemblies can overwrite default functionality.

.. py:module:: database.views

.. autofunction:: store

Database statistics
-------------------

The database app also exposes an API-function for loading database statistics of the user. The statistics are:

- 'time_budget': Sum of all the CPU time (in seconds) used by the user.
- 'storage_budget': Integral over the storage the user user over time. The value is in bytes*seconds.
- 'current_storage': The amount of of storage (in bytes) the user uses at the moment.
- 'last_calculation': Timestamp of the last time the budgets were calculated. This is needed if the frontend
  tries to calculate the storage budget up to the current time.
- 'assembly_count': Number of assemblies the user owns.
- 'installed_assemblies_count': Number of assemblies the user has installed.
- 'all_assemblies_count': Number of assemblies available for the user.

.. autofunction:: statistics
