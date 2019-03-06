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
from pony.orm.core import Collection
from warnings import warn


class LazyEntityMeta(type):
    def __new__(mcs, name, parents, attrs, database=None):
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
                    mcs._entities[database][v.py_type].__attrs__[v.reverse] = r
                elif v.py_type in mcs._reverse[database]:
                    mcs._reverse[database][v.py_type][v.reverse] = r
                else:
                    mcs._reverse[database][v.py_type] = {v.reverse: r}
                attrs[k] = v

        if name in mcs._reverse[database]:
            for k, v in mcs._reverse[database].pop(name).items():
                attrs[k] = v

        entity = mcs._entities[database][name] = LazyEntity(parents, attrs)
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
            if hasattr(lazy, 'entity'):
                raise RuntimeError('entity already attached')

            attrs = lazy.__attrs__
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

            lazy.entity = type(name, (db.Entity, *lazy.__parents__), attrs)

    _entities = {}
    _reverse = defaultdict(dict)


class DoubleLink:
    def __init__(self, attr, reverse):
        if not attr.reverse:
            raise AttributeError('reverse attribute required')
        self.reverse = reverse
        self.attr = attr


class LazyEntity:
    __slots__ = ('__parents__', '__attrs__', 'entity')

    def __init__(self, bases, attrs):
        self.__parents__ = bases
        self.__attrs__ = attrs

    def __call__(self, *args, **kwargs):
        return self.entity(*args, **kwargs)

    def __getitem__(self, item):
        return self.entity[item]

    def __repr__(self):
        return repr(self.entity)

    def __str__(self):
        return str(self.entity)

    def __getattr__(self, item):
        if item == 'entity':
            raise AttributeError
        return getattr(self.entity, item)
