#!/usr/bin/env python

import os.path
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setupconf = dict(
    name = 'aldjemy',
    version = "0.3.3",
    license = 'BSD',
    url = 'https://github.com/Deepwalker/aldjemy/',
    author = 'Mihail Krivushin',
    author_email = 'krivushinme@gmail.com',
    description = ('SQLAlchemy to Django integration library'),
    long_description = read('README.rst'),

    packages = find_packages(),

    install_requires = ['sqlalchemy>0.7.1'],

    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
    )

if __name__ == '__main__':
    setup(**setupconf)
