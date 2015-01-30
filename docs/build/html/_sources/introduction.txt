Introduction
============

Pinyto is your own private and secure database. You decide which data is used for which application
and how the data is processed even before it reaches the device. It achieves that with a document
based database (MongoDB) which saves your data in the structure you want it to have. You can access
your data through Assemblies which process and prepare your data at the server before it gets
transferred to an app on a device. It is up to you which Assemblies you want to install and you can
even create your own Assemblies by programming them in Python. This structure lets you expose the
minimum of your data to achieve just what you want. Assemblies can also do things on their own like
searching for data on the internet to complete your saved datasets computationally on the server.
This structure lets your apps feel smart because they can access the information they need while
keeping your data in your control. Assemblies are always OpenSource and you can read their sourcecode
if you want to know what they are doing.

Pinyto is designed as a framework to make our vision of a personal cloud accessible for you. We
provide some webapps and applications for your devices to show how Pinyto is meant to be used and
what it is capable of. They may also be useful as they are.

Structure
---------

There are two main parts of the Pinyto-Cloud component hosted on your server:

1. The Django application talking to your database and executing code from the assemblies.
2. The Webapps which are hosted on the server.

The Django application is structured in six Django-Apps:

1. **pinytoCloud** is the main app which contains the settings.py and the main urls.py. Its models.py
   contains all the models used for administration of your personal cloud. This data is saved in the
   SQL-database specified in settings.py. Your user-data does not live in this database. views.py
   contains the views used for administration of the cloud including registration and authentication.
2. **keyserver** contains models and views which are needed to access the cloud with username and
   password. Pinyto normally uses public-key-authentication which is not usable for webapps. The
   keyserver does the public-key-authentication for all users who supply the correct credentials. The
   models in this app store private keys and password hashes for user accounts.
3. **database** wraps all calls to the document based database used to store the data. It uses pymongo
   but adds some functionality specific for Pinyto.
4. **service** contains helpers which can be called from assemblies to perform certain tasks. As
   assemblies are very limited in their ability to process data all the work is done in those services.
5. **api_prototype** contains the views handling all requests concerning api-calls and jobs at
   assemblies. If necessary a sandbox is initialized and code from the assemblies is executed there.
6. **api** contains trusted assemblies which are executed without a sandbox. This is generally not
   necessary but can improve the performance of assembly calls and job execution.

The Webapps are structured in folders matching the name of the assembly. For example the files for the
"pinyto/Todo" assembly live in /webapps/pinyto/Todo/. Every webapp is a separate application which
is bootstrapped with its index.html. At the moment all Webapps are based on Angular.js and are
structured like typical Angular applications.