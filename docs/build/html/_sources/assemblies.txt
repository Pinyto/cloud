Assemblies
==========

Assemblies are the key element of Pinyto as they empower the user to do with her data as she likes. Users
can write their own assemblies but they also can install assemblies from other users. If those other users
update their assembly the user automatically uses the new version without having to change anything.

.. warning::
    It is crucial that users can trust the authors of the assemblies they have installed. They can check
    the sourcecode of the all assemblies as they install them but if an update changes the assembly the
    user gets no notification and the changed assembly may leak or delete data.

    Users can prevent that by forking assemblies of other users which makes the assembly in the state as it
    is one of their own. By doing that their assembly does not change if the original author changes her
    assembly and the user can be sure that no harmful code is executed. This method has the downside that
    updates with bugfixes or new features do not get installed automatically. The user may delete the forked
    assembly in case of a good update and fork the original again. The usability of this procedure could be
    improved in future versions.

Installing assemblies
---------------------

If you run your own Pinyto server there are two ways to install new assemblies. The first possibility is to
store them in your database. You may want to create user accounts to have telling names for the assemblies.
For example for the assembly ``pinyto/Todo`` a user with the name "pinyto" must be present.

If you check out a new version of Pinyto there might be new default assemblies in the ``api`` module. With this
version come three bundled assemblies:

- **pinyto/DocumentsAdmin** is used for the backoffice to let you browse all your documents there.
- **pinyto/Todo** is the assembly for the example app for Pinyto which is a simple TODO-list.
- **bborsalino/Librarian** is an assembly for a app used to manage the books in your flat. This assembly
  uses a job which completes incomplete data for books by asking a publicly available database. This could be
  a good example for your next assembly because the TODO-app does not need a job.

The assemblies in the ``api`` module provide data migrations which insert the user and the assembly itself into
the database.

Normally the code of every assembly gets executed in a seccomp secured sandbox. Using the sandbox might decrease
the performance of the assembly execution. So Pinyto gives administrators the opportunity to install assemblies
as Django apps inside the ``api`` module. If an assembly is called and a directly installed assembly in the
``api`` module is found the code from there gets executed without a sandbox. In order to have this working
an assembly with the same name has to exist in the database.

.. warning::
    A bad admin could trick users in thinking that an assembly is not harmful by having different code saved
    in the database than in the Django app in ``api``. We considered this a minor threat because if your admin
    wants to harm you she could do all sorts of bad things to your data. It is certainly best to have an admin
    you can trust. If you do not trust your admin become your own admin on your own server.

    If you write an assembly inside of ``api`` make sure to insert the correct code of the assembly in the data
    migration.

For users there is no visible difference between assemblies executed in the sandbox and assemblies executed
directly. If you have benchmarks showing how big the difference is please share them.

Calling Assemblies
------------------

.. py:module:: api_prototype.views

Assemblies are called with the ``api_call`` view in the ``api_prototype`` module.

.. autofunction:: api_call

``api_call`` checks in the ``api`` module if there is a directly executable version of the assembly. If there
is none ``load_api`` is called.

.. autofunction:: load_api

Executing Jobs
--------------

API calls can save documents of different type. The "type": "job" is special as it is the type of a document
describing a scheduled job. A job scheduled this way gets executed immediately after the request saving the
document is finished. The scheduling document must have the following structure:

- "type": "job"
- "data": A dictionary containing the following attributes and data:

  - "assembly_user": The username of the author of the assembly.
  - "assembly_name": The name of the assembly.
  - "job_name": The name of the job.

After each finished request Django calls ``check_for_jobs``.

.. autofunction:: check_for_jobs

The Sandbox
-----------

.. py:module:: api_prototype.sandbox

The Pinyto sandbox is used if ``safely_exec`` is called.

.. autofunction:: safely_exec

``safely_exec`` starts a process and executes ``sandbox`` there.

.. autofunction:: sandbox

The process executing ``sandbox`` creates a new instance of ``SecureHost``. The initialization of this class
forks the sandbox process into two parts:

1. The host process which has access to the database the request and the services.
2. The child which has only a pipe to communicate to the host process. All open file descriptors in the child
   process get closed and the database, request and service objects get replaced by sandbox versions. Those
   sandbox versions of the services have the same signatures but communicate only to the host process which
   asks the real services for answers which get returned into the child process. This is done because the
   sandbox is secured using *seccomp* and seccomp only allows reading an writing to already open file
   descriptors. The access to any other function of the kernel is blocked by the kernel. If the exec call
   in the child process tries to do anything other than calculations with the data in its memory or
   communication to the services over the pipe to the host process it will get terminated by the kernel.

.. py:module:: api_prototype.seccomp_process

.. autoclass:: SecureHost
   :members:

There are some helper functions and classes which may be relevant for understanding how the sandbox works:

.. py:module:: api_prototype.sandbox_helpers

.. autofunction:: libc_exit

.. autofunction:: read_exact

.. autofunction:: write_exact

.. autofunction:: write_to_pipe

.. autofunction:: read_from_pipe

.. autofunction:: escape_all_objectids_and_datetime

.. autofunction:: unescape_all_objectids_and_datetime

.. autofunction:: piped_command

.. autoclass:: NoResponseFromHostException
   :members:

.. py:module:: api_prototype.models

.. autoclass:: SandboxCollectionWrapper
   :members:

.. autoclass:: SandboxRequestPost
   :members:

.. autoclass:: SandboxRequest
   :members:

.. autoclass:: CanNotCreateNewInstanceInTheSandbox
   :members:

.. autoclass:: Factory
   :members:

.. autoclass:: SandboxParseHtml
   :members:

.. autoclass:: SandboxHttp
   :members:

.. py:module:: api_prototype.sandbox_helpers

.. autoclass:: EmptyRequest
   :members: