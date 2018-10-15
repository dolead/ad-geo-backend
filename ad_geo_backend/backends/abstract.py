import logging
from abc import ABCMeta, abstractmethod, abstractclassmethod

logger = logging.getLogger(__name__)


class AbstractGeoBackend:
    __metaclass__ = ABCMeta

    def __init__(self, network):
        self.network = network

    @abstractclassmethod
    def set_connection(cls, host, db_name, **credentials):
        return None

    @abstractmethod
    def list(self, criteria, sort=None, limit=None):
        return []

    @abstractmethod
    def get(self, criteria):
        return None

    @abstractmethod
    def insert_many(self, objects):
        return None

    def get_parent(self, geo_model):
        return self.get({'dolead_id': geo_model.parent_id})

    def list_children(self, geo_model, **filters):
        filters['parent_id'] = geo_model.dolead_id
        return self.list(filters)

    def list_ancestors(self, geo_model):
        def get_parent(model):
            parent = self.get_parent(model)
            if not parent:
                return
            yield from get_parent(parent)
            yield parent
        yield from get_parent(geo_model)

    def list_heirs(self, geo_model, **filters):
        for child in self.list_children(geo_model):
            yield from self.list_heirs(child, **filters)
        yield from self.list_children(geo_model, **filters)
