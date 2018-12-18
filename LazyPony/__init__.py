# -*- coding: utf-8 -*-
#
#  Copyright 2018 Ramil Nugmanov <stsouko@live.ru>
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
from collections import defaultdict


class LazyEntityMeta(type):
    def __new__(mcs, name, bases, attrs):
        if name in mcs._entities:
            raise TypeError('Entity already exists')

        for k, v in attrs.items():
            if isinstance(v, DoubleLink):
                r = v.reverse
                v = v.attr
                if v.py_type in mcs._entities:
                    mcs._entities[v.py_type].attrs[v.reverse] = r
                else:
                    mcs._reverse[v.py_type][v.reverse] = r
                attrs[k] = v

        if name in mcs._reverse:
            for k, v in mcs._reverse.pop(name).items():
                attrs[k] = v

        entity = mcs._entities[name] = LazyEntity(bases, attrs)
        return entity

    @classmethod
    def attach(mcs, db, schema=None):
        for name, lazy in mcs._entities.items():
            if schema in lazy.databases:
                raise RuntimeError('schema already attached')
            attrs = lazy.attrs.copy()
            if schema:
                if '_table_' in attrs:
                    attrs['_table_'] = (schema, attrs['_table_'])
                else:
                    attrs['_table_'] = (schema, name)
            lazy.databases[schema] = type(name, lazy.bases + (db.Entity,), attrs)

    _entities = {}
    _reverse = defaultdict(dict)


class DoubleLink:
    def __init__(self, attr, reverse):
        if not attr.reverse:
            raise AttributeError('reverse attribute required')
        self.reverse = reverse
        self.attr = attr


class LazyEntity:
    def __init__(self, bases, attrs):
        self.bases = bases
        self.attrs = attrs
        self.databases = {}

    def __getitem__(self, item):
        return self.databases[item]
