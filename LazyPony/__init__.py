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
from collections import defaultdict
from itertools import chain
from pony.orm.core import Attribute, Collection
from warnings import warn


class LazyEntityMeta(type):
    def __new__(mcs, name, bases, attrs, database=None):
        if database not in mcs._entities:
            mcs._entities[database] = {}
            mcs._reverse[database] = {}
        if name in mcs._entities[database]:
            raise TypeError('Entity already exists')

        for k, v in attrs.items():
            if isinstance(v, DoubleLink):
                r = v.reverse
                v = v.attr
                if v.py_type in mcs._entities[database]:
                    mcs._entities[database][v.py_type].attrs[v.reverse] = r
                elif v.py_type in mcs._reverse[database]:
                    mcs._reverse[database][v.py_type][v.reverse] = r
                else:
                    mcs._reverse[database][v.py_type] = {v.reverse: r}
                attrs[k] = v

        if name in mcs._reverse[database]:
            for k, v in mcs._reverse[database].pop(name).items():
                attrs[k] = v

        entity = mcs._entities[database][name] = LazyEntity(bases, attrs)
        return entity

    @classmethod
    def attach(mcs, db, schema=None, database=None):
        """

        :param db: Database() object
        :param schema: schema name. useful for postgres
        :param database: need for separation of Database() objects. By default all entities will be in single Database.
        pass database argument in class definition for grouping entities.

        class A(metaclass=LazyEntityMeta, database='db1'):
            pass
        """
        for name, lazy in mcs._entities[database].items():
            if schema in lazy.databases:
                raise RuntimeError('schema already attached')

            attrs = lazy.attrs.copy()
            for attrs_key, attrs_value in attrs.items():
                if isinstance(attrs_value, Attribute):  # deepcopy not working
                    copy_attrs_value = Attribute.__new__(type(attrs_value))
                    for key in chain.from_iterable(getattr(cls, '__slots__', []) for cls in type(attrs_value).__mro__):
                        if hasattr(attrs_value, key):
                            value = getattr(attrs_value, key)
                            if isinstance(value, dict):
                                value = value.copy()
                            setattr(copy_attrs_value, key, value)
                    attrs[attrs_key] = copy_attrs_value

            if schema:
                if '_table_' in attrs:
                    if not isinstance(attrs['_table_'], tuple):  # if tuple: schema hardcoded
                        attrs['_table_'] = (schema, attrs['_table_'])
                else:
                    attrs['_table_'] = (schema, name)
                for k, v in attrs.items():
                    # if schemas used, need predefined name of m2m table.
                    if isinstance(v, Collection):
                        if v.table:
                            v.table = (schema, v.table)
                        else:
                            warn('for many-to-many relationship if schema used NEED to define m2m table name')

            lazy.databases[schema] = type(name, (db.Entity, *lazy.bases), attrs)

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
