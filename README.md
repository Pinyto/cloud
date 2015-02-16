This is the Pinyto Backend. Install this application on your server and use its url at the pinyto
clients on your devices to connect to it.

What is Pinyto?
===============

Your contacts are at Google, your conversations at Facebook and your documents in a Dropbox. But 
although those big corporations earn a lot of money with your data it does not work well together?

Instead of working productively you fiddle with USB cables, sync data with providers you do not trust 
and in the end you type the details of your next meeting from one device to the next because this 
method still works best.

Pinyto could solve all those problems for you because Pinyto is not about earning money but the idea. 
If you want to access the same personal data from different devices you need your own private cloud. 
And because the data we produce in our every day work tells a lot about us we need total control over 
this data and when and by whom it is accessed. At the same time we want smart devices which access our 
data and learn from it to help us - every day.

Pinyto offers you your own private and secure database. You decide which data is used for which 
application and how the data is processed even before it reaches the device. It achieves that with a 
document based database (MongoDB) which saves your data in the structure you want it to have. You can 
access your data through Assemblies which process and prepare your data at the server before it gets 
transferred to an app on a device. It is up to you which Assemblies you want to install and you can 
even create your own Assemblies by programming them in Python. This structure lets you expose the 
minimum of your data to achieve just what you want. Assemblies can also do things on their own like 
searching for data on the internet to complete your saved datasets computationally on the server. 
This structure lets your apps feel smart because they can access the information they need while 
keeping your data in your control. Assemblies are always OpenSource and you can read their 
sourcecode if you want to know what they are doing.

Pinyto is designed as a framework to make our vision of a personal cloud accessible for you. We 
provide some webapps and applications for your devices to show how Pinyto is meant to be used and 
what it is capable of. They may also be useful as they are.

Installation
============

For installing Pinyto you need a server which runs Python and Django. There are some hosters which 
offer webspace where this is possible but mostly you will need your own virtual- or root-server. 
We recommend using a debian-based system for this server like [Ubuntu](http://www.ubuntu.com/) but 
it can run on any systems which meets the requirements:

* You will need [seccomp-support](https://en.wikipedia.org/wiki/Seccomp) in your kernel. Linux has 
  that since 2009 but BSD and Windows-Kernel probably do not have this feature and will not be able 
  to run the Pinyto sandbox.
* [Nginx](http://nginx.org/) or [Apache](http://httpd.apache.org/) for serving static files. There 
  are no complicated requirements so the stable version of your system is fine. However if you plan 
  to use SPDY or HTTP 2.0 you may need a more recent version.
* You need a SQL database for Pinyto. You may use [SQLite](http://www.sqlite.org/) which is file 
  based and very easy to install. For installations with a lot of users 
  [PostgreSQL](http://www.postgresql.org/) is recommended. For a full description of which database 
  can be used see the [Django documentation](https://docs.djangoproject.com/en/1.6/ref/databases/).
* [Django](https://www.djangoproject.com/download/) 1.7 or newer. You need a wsgi-wrapper to pass 
  requests to Django. We recommend using [uWSGI](http://projects.unbit.it/uwsgi/). Installation 
  instructions for this setup are 
  [here](https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/uwsgi/).
* [MongoDB](http://www.mongodb.org/) 2.4.9 or newer
* [Python](https://www.python.org/) 3.4 or newer
* [PyMongo](http://api.mongodb.org/python/current/installation.html)

Setting up a virtualenv
-----------------------
We recommend using a virtualenv which can be created with ``virtualenv venv -p /usr/bin/python3``. 
After activating the virtual environment with ``source venv/bin/activate`` you can install the
following dependencies with ``pip3 install <packet>``:

* `django`
* `cryptography`
* `django-cors-headers`
* `cffi`
* `pymongo`
* `beautifulsoup4`
* `pytz`
* `python-prctl`
* `requests`

This is optional. You only need this theme if you want to build the documentation yourself:

* `sphinx_rtd_theme`

This will install all requirements: ``pip install -r requirements.txt``

Developing Pinyto
=================

Pinyto is free Software licensed under the [GPL v.3](http://www.gnu.org/copyleft/gpl.html). You 
are free to distribute and modify Pinyto to match your needs. Pinyto is written in 
[Python](https://www.python.org/) using the famous [Django](https://www.djangoproject.com/) 
framework. [MongoDB](http://www.mongodb.org/) is used to store the user's data but for 
administrative purposes there is also a SQL Database needed. Pinyto's default backoffice is 
created with [Angular](https://angularjs.org/) which proved itself very handy for developing 
webapps which use Pinyto.

Contributing
------------

The core functionality is working and there are some automatic tests which cover more than 80% of 
the code. Since Pinyto is meant to be a safe place to store precious personal data additional efforts 
to improve test coverage and overall code quality should be made.

Pinyto will reach version 2.0 if the following features are all working: (~~those are done~~)

* ~~Saving of user data in a schema-free, easily queryable form~~
* ~~Users can write own code in a secure sandbox which is executed at the server~~
* ~~Assemblies with pre-packaged code for certain use cases can easily be installed and removed~~
* ~~Monitoring of used disk space and computation time~~
* ~~Secure authentication for webapps and apps for devices (on the device without password)~~
* Permission management enabling users to make data accessible and editable for others
* A cloud synced ToDo-list for different devices (desktop, phone, web)
* Contacts (especially the ones on Android phones) can be managed through Pinyto
* A cloud synced calendar which notifies the user on time for dates
* A synced messenger which combines instant messages with mail in one place

Feel free to contribute to any of these projects. We are planning to support Linux desktops and 
Android smartphones but it would be great if somebody brought Pinyto to Windows, Mac or iOS. Even if 
the backend is open-source the apps for the devices do not need to be free. However the daemon 
handling the connections to the cloud should probably be open-source so users can trust that they do 
not do something funny.

Please [contact us](mailto:jonny@pinyto.de) if you are developing an app using Pinyto. We would like 
to link to your project page.

If you want to help with the backend or any of the existing apps please subscribe to the 
[mailing-list](http://lists.pinyto.de/mailman/listinfo/pinyto).
