Presentation
============

Django graffle is a Django app that provides a management command called
``graffle``. This command uses Omnigraffle in order to produce a graph of your
models and their relationships.

Forget complicated tools, write your models and graph them for your boss.

Installation
============

First, install `appscript <http://appscript.sourceforge.net/>`_.

Download source code and run ``python setup.py install``. Then, Add
``django_graffle`` to your ``INSTALLED_APPS`` in your project.

Usage
=====

In you project, run ``python manage.py graffle``. If you want to graph only
some apps, specify their names on command line. The command looks for an OS X
App called "Omnigraffle Professional 5". You can change it with
``--omnigraffle`` option.

License
=======

Django graffle is released under the BSD license. See the LICENSE
file for the complete license.
