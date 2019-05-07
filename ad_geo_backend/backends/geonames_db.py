from pymongo import ASCENDING
from .mongodb import MongoBackend
from ad_geo_backend.model import GeonamesModel


class MongoGeonamesBackend(MongoBackend):
    __indexes = {
        'geoname_id': {'unique': True},
    }
    model = GeonamesModel

    def check_indexes(self):
        for idx, options in self.__indexes.items():
            options = options or {}
            self.collection.ensure_index(idx, **options)
