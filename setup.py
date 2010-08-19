# -*- coding: utf-8 -*-
#
# This file is part of Django graffle released under the BSD license.
# See the LICENSE for more information.

from setuptools import setup, find_packages

version = '0.5'
packages = ['django_graffle'] + ['django_graffle.%s' % x for x in find_packages('django_graffle',)]

setup(
    name='django_graffle',
    version=version,
    description='Graph your django views with Omnigraffle.',
    author='Olivier Meunier',
    author_email='om@neokraft.net',
    url='http://bitbucket.org/cedarlab/django-graffle/',
    packages=packages,
    classifiers=[
        'Development Status :: %s' % version,
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
