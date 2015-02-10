#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


__version__ = '0.1.0'
readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


install_requires = [
    'Flask==0.10.1',
    'Flask-Admin==1.0.9',
    'Flask-Mongoengine==0.7.1',
    'Eve-Mongoengine==0.0.9',
    'Eve-Docs',
    'enum34==1.0.4',
    'redis==2.10.3',
    'requests==2.5.1',
]
tests_require = install_requires + [
    'pytest==2.6.4', 'coverage==3.7.1', 'mock==1.0.1']
develop_require = tests_require + [
    'Sphinx>=1.2.1', 'sphinxcontrib-httpdomain']


setup(
    name='pancake',
    version=__version__,
    description='',
    long_description=readme + '\n\n' + history,
    author='Detalytics',
    author_email='developer@detalytics.com',
    url='https://github.com/tryagainconepts/pancake',
    packages=find_packages(),
    package_dir={'pancake': 'pancake'},
    install_requires=install_requires,
    extras_require={
        'develop': develop_require,
        'test': tests_require,
    },
    zip_safe=False,
    keywords='pancake',
	entry_points={
		'console_scripts': [
			'pancaked = pancake.app:main'
		]
	},
)
