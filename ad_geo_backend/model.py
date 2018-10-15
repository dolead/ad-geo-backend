class GeoModel:

    def __init__(self, backend, name, dolead_id, publisher_id, **kwargs):
        self._backend = backend
        self.name = name
        self.dolead_id = dolead_id
        self.publisher_id = publisher_id

        self.slug = kwargs.get('slug')
        self.geo_type = kwargs.get('geo_type')
        self.parent_id = kwargs.get('parent_id')
        self.canonical_name = kwargs.get('canonical_name')
        self.country_code = kwargs.get('country_code')

        self.latitude = kwargs.get('latitude')
        self.longitude = kwargs.get('longitude')

    @property
    def bing_id(self):
        return self.publisher_id

    @property
    def adwords_id(self):
        return self.publisher_id

    @property
    def name_full(self):
        """Get full name including hierarchy"""
        return ', '.join(reversed([p.name
                for p in self._backend.list_ancestors(self)]))

    @property
    def parent(self):
        return self._backend.get({'dolead_id': self.parent_id})

    def __str__(self):
        return "<%s #%s [%s] %s>" % (self.geo_type, self.dolead_id,
                                     self.country_code, self.name)

    def __repr__(self):
        return str(self)

    def __iter__(self):
        for child in self._backend.list_children(self):
            yield child

    def __hash__(self):
        return hash(self.dolead_id)

    def __getitem__(self, key, default=None):
        return getattr(self, key, default)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def dump(self):
        return {'name': self.name,
                'dolead_id ': self.dolead_id,
                'publisher_id': self.publisher_id,

                'slug': self.slug,
                'geo_type': self.geo_type,
                'parent_id': self.parent_id,
                'canonical_name': self.canonical_name,
                'country_code': self.country_code,

                'latitude': self.latitude,
                'longitude': self.longitude}
