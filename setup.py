#!/usr/bin/env python
# coding: utf-8
import sys


setup_data = {
    'name': 'django-replicated2',
    'version': __import__('django_replicated2').__version__,
    'description': 'Django DB router for stateful master-slave replication',
    'packages': ['django_replicated2', 'django_replicated2.tests'],
    'platforms': "All",
    'classifiers': [
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        ],
}

setuptools_extensions = {
    'zip_safe': True,
    'test_suite': "runtests.runtests",
    #'include_package_data': True,
}

if 'develop' in sys.argv:
    setup_data['scripts'] = ['runtests.py']

try:
    from setuptools import setup
    setup_data.update(setuptools_extensions)
except ImportError:
    print("Cannot load setuptool, revert to distutils")
    from distutils.core import setup

setup(**setup_data)
