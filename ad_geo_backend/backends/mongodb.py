# -*- coding: utf8 -*-
import logging

from pymongo import MongoClient
from pymongo.database import Database

from ad_geo_backend.backends.abstract import AbstractGeoBackend
from ad_geo_backend.model import GeoModel

logger = logging.getLogger(__name__)


class MongoBackend(AbstractGeoBackend):
    __connection = None
    __db_name = None
    __collection_prefix = 'ad_geo_backend'
    __indexes = {
        'dolead_id': {'unique': True},
        'name': None,
        'slug': None,
        'canonical_name': None,
        'country_code': None,
        'parent_id': None,
        'publisher_id': None,
    }

    @classmethod
    def set_connection(cls, host, db_name, **credentials):
        if cls.__connection is None:
            cls.__connection = MongoClient(host)
            cls.__db_name = db_name
            if len({'name', 'password'}.intersection(credentials)) == 2:
                cls.get_database().authenticate(**credentials)

    def list(self, criteria, sort=None, limit=None):
        query = self.collection.find(criteria)
        if sort:
            query.sort(sort)
        if limit:
            query.limit(limit)
        for l in query:
            yield GeoModel(self, **l)

    def get(self, criteria):
        item = self.collection.find_one(criteria)
        return GeoModel(self, **item) if item else item

    def insert_many(self, objects):
        return self.collection.insert(objects)

    def reset(self):
        return self.collection.drop()

    # Mongo specific methods

    @classmethod
    def get_database(cls):
        if not cls.__connection:
            raise RuntimeError('Please set an MongoDB connection first')
        return Database(cls.__connection, cls.__db_name)

    @property
    def collection(self):
        return getattr(self.get_database(),
                '%s_%s' % (self.__collection_prefix, self.network.lower()))

    def check_indexes(self):
        for idx, options in self.__indexes.items():
            options = options or {}
            self.collection.ensure_index(idx, **options)
