#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Copyright 2018, 2019 Ramil Nugmanov <stsouko@live.ru>
#  This file is part of LazyPony.
#
#  LazyPony is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, see <https://www.gnu.org/licenses/>.
#
from pathlib import Path
from setuptools import setup


version = '0.2.1'


setup(
    name='LazyPony',
    version=version,
    packages=['LazyPony'],
    url='https://github.com/stsouko/LazyPony',
    license='LGPLv3',
    author='Dr. Ramil Nugmanov',
    author_email='stsouko@live.ru',
    python_requires='>=3.6.7',
    install_requires=['pony>=0.7.9'],
    long_description=(Path(__file__).parent / 'README.md').open().read(),
    classifiers=['Environment :: Plugins',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 3 :: Only',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: Software Development',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Software Development :: Libraries :: Python Modules']
)
